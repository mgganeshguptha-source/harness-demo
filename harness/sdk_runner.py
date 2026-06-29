"""
sdk_runner.py — the REAL AgentRunner, backed by the Copilot SDK.

This is the only file that talks to Copilot. It satisfies the same AgentRunner
protocol as FakeAgentRunner, so the state machine / executor / boundaries are
unchanged. Swapping fake -> real is a one-line change in run.py.

TWO LAYERS OF THE HARNESS MEET HERE:
  * CAPABILITY (probabilistic): the prompt is built from the user story + your
    .github/skills + .github/instructions. This is the "Markdown gives capability".
  * GUARANTEE (deterministic): on_permission_request enforces the phase write
    boundary in REAL TIME. Every file write the model attempts is checked against
    is_write_allowed() for the current phase; out-of-bounds => denied at the SDK,
    before it touches disk. This is the "code gives a guarantee".

Requires: pip install github-copilot-sdk ; Copilot CLI authed (Pro license).
Python 3.11+.
"""
from __future__ import annotations
import asyncio
from pathlib import Path

from phases import Phase
from state import RunState
from executor import AgentResult
from boundaries import is_write_allowed, deny_reason

# SDK imports are done lazily inside run() so the rest of the harness (and all the
# zero-credit tests) import cleanly on machines without the SDK installed.


# Default model for the PoC. "cheapest" — override via HarnessConfig later.
# NOTE: verify the exact string with client.list_models() on your tenant; model
# availability differs by org/subscription.
DEFAULT_MODEL = "gpt-4.1"


def _parse_frontmatter_applyto(text: str) -> str | None:
    """Extract the applyTo value from an instruction file's YAML frontmatter.
    Returns the raw glob string (may be comma-separated), or None if absent."""
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    fm = text[3:end]
    for line in fm.splitlines():
        line = line.strip()
        if line.startswith("applyTo:"):
            val = line.split(":", 1)[1].strip().strip('"').strip("'")
            return val
    return None


def _glob_intersects_scope(apply_to: str, scope_globs: list) -> bool:
    """Does an instruction's applyTo intersect the phase's file scope?
    '**' always matches (always-on guardrail). Otherwise check prefix overlap
    between the applyTo patterns and the phase scope patterns."""
    patterns = [p.strip() for p in apply_to.split(",") if p.strip()]
    for pat in patterns:
        if pat == "**":
            return True
        # reduce a glob to its literal directory prefix for a coarse overlap test
        pat_prefix = pat.split("*", 1)[0].rstrip("/")
        for sc in scope_globs:
            sc_prefix = sc.split("*", 1)[0].rstrip("/")
            if not pat_prefix or not sc_prefix:
                continue
            if pat_prefix.startswith(sc_prefix) or sc_prefix.startswith(pat_prefix):
                return True
    return False


def _extract_names(data, *attr_candidates) -> list[str]:
    """Defensively pull human-readable name(s) out of an SDK event payload.

    The SDK's event schema (github-copilot-sdk 1.0.x) isn't documented for the
    skills_loaded / tool.execution_* payloads, and the shape differs by event.
    Rather than hard-code one attribute, we try several shapes in order:
      1. a list attribute (e.g. data.skills) of objects/dicts each having a name
      2. a scalar name attribute (e.g. data.name / data.tool_name) on data itself
      3. a pydantic .model_dump() fallback, scanning common keys
    Returns a de-duplicated, order-preserving list of strings (possibly empty).
    """
    out: list[str] = []

    def _name_of(obj) -> str | None:
        for k in ("name", "id", "tool_name", "skill_name", "title"):
            v = getattr(obj, k, None)
            if v is None and isinstance(obj, dict):
                v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        if isinstance(obj, str) and obj.strip():
            return obj.strip()
        return None

    # 1) list-shaped attributes (skills, tools, ...)
    for attr in attr_candidates:
        seq = getattr(data, attr, None)
        if seq is None and isinstance(data, dict):
            seq = data.get(attr)
        if isinstance(seq, (list, tuple)):
            for item in seq:
                n = _name_of(item)
                if n:
                    out.append(n)

    # 2) scalar name directly on data (tool.execution_start is usually one tool)
    if not out:
        n = _name_of(data)
        if n:
            out.append(n)

    # 3) pydantic dump fallback — last resort, scan likely keys
    if not out:
        dump = None
        try:
            dump = data.model_dump()  # pydantic v2
        except Exception:
            try:
                dump = dict(vars(data))
            except Exception:
                dump = None
        if isinstance(dump, dict):
            for attr in attr_candidates:
                seq = dump.get(attr)
                if isinstance(seq, (list, tuple)):
                    for item in seq:
                        n = _name_of(item)
                        if n:
                            out.append(n)
            for k in ("name", "tool_name", "skill_name"):
                v = dump.get(k)
                if isinstance(v, str) and v.strip():
                    out.append(v.strip())

    # de-dupe, preserve order
    seen = set()
    deduped = []
    for n in out:
        if n not in seen:
            seen.add(n)
            deduped.append(n)
    return deduped


def _load_capability_layer(repo_root: Path, phase: Phase) -> str:
    """Load the capability layer for THIS phase.

    Config-driven (HarnessConfig):
      - selective_capability=False -> load everything (legacy behaviour).
      - always-on guardrails: instruction files with applyTo "**".
      - phase-scoped instructions: applyTo glob intersects phase_file_scope[phase].
      - phase skills: the named skills in phase_skills[phase].

    This keeps cross-cutting guardrails (HIPAA, prompt-injection, logging,
    output-naming) in EVERY phase, while stack/phase-specific rules and skills
    load only where relevant — cutting tokens without dropping safety rules.
    """
    from config import HarnessConfig
    cfg = HarnessConfig.load(repo_root / ".harness")
    gh = repo_root / ".github"
    chunks = []

    # ---- instructions ----
    instr_dir = gh / "instructions"
    if instr_dir.is_dir():
        scope = cfg.phase_file_scope.get(phase.id, []) if cfg.selective_capability else None
        stacks = cfg.repo_stacks or []
        include_all_stacks = (not stacks) or ("*" in stacks)
        for md in sorted(instr_dir.rglob("*.md")):
            # REPO-LEVEL STACK FILTER: if this file sits in a stack subfolder
            # (backend/, angular-frontend/, mobile-frontend/) that this repo does
            # not contain, skip it entirely — before any phase logic. Files
            # directly under instructions/ have no stack subfolder => always kept.
            rel_parent = md.parent.relative_to(instr_dir)
            stack_folder = rel_parent.parts[0] if rel_parent.parts else None
            if (cfg.selective_capability and not include_all_stacks
                    and stack_folder is not None and stack_folder not in stacks):
                continue
            try:
                text = md.read_text(encoding="utf-8")
            except Exception:
                continue
            if cfg.selective_capability:
                apply_to = _parse_frontmatter_applyto(text)
                # no applyTo -> treat as always-on (safe default)
                if apply_to is None or apply_to == "**":
                    pass  # always-on guardrail
                elif _glob_intersects_scope(apply_to, scope):
                    pass  # relevant to this phase
                else:
                    continue  # skip — not relevant to this phase
            chunks.append(f"\n--- instructions/{md.name} ---\n{text}")

    # ---- skills ----
    skills_dir = gh / "skills"
    if skills_dir.is_dir():
        if cfg.selective_capability:
            wanted = set(cfg.phase_skills.get(phase.id, []))
        else:
            wanted = None  # all
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            skill_name = skill_md.parent.name
            if wanted is not None and skill_name not in wanted:
                continue
            try:
                chunks.append(f"\n--- skill: {skill_name} ---\n" + skill_md.read_text(encoding="utf-8"))
            except Exception:
                pass

    return "\n".join(chunks)


def _phase_instruction(phase: Phase, run: RunState, repo_root: Path) -> str:
    """The per-phase task prompt. Phase-specific, story-aware, feedback-aware.

    All output paths are given as ABSOLUTE paths derived from repo_root. In a
    monorepo the agent may otherwise resolve a relative '.github/...' against the
    git root (one level up) instead of the service folder; absolute paths remove
    that ambiguity. We also tell the agent the directory already exists and that
    shell is disallowed, so it writes the file directly without attempting mkdir.
    """
    story = run.story
    rr = str(repo_root).replace("\\", "/").rstrip("/")
    ctx_dir = f"{rr}/.github/story-context-files"
    plan_file = f"{rr}/.harness/prompt-steps.md"
    src_main = f"{rr}/src/main"
    src_test = f"{rr}/src/test"
    docs_dir = f"{rr}/docs"
    pr_body = f"{rr}/.harness/pr-body.md"

    base = {
        "context": (
            f"You are running in NON-INTERACTIVE / CI mode. Do NOT ask any questions "
            f"and do NOT wait for input. Use the build-context skill in CI mode.\n"
            f"Explore the repository (read-only) and write a context document as a new "
            f"timestamped .md file in this EXACT directory (it ALREADY EXISTS, do not "
            f"mkdir, shell is disallowed): {ctx_dir}\n"
            f"  STORY: {story}\n"
            f"Fill every section you can from the story. For any genuine ambiguity, write a "
            f"precise '[NEEDS CLARIFICATION]: <missing dimension>' line in Section 8 — do NOT "
            f"guess and do NOT use vague language. Do NOT modify any source files. "
            f"Write ONLY the single context .md file in {ctx_dir}."
        ),
        "prompt_steps": (
            f"You are running in NON-INTERACTIVE / CI mode. Use the build-prompt-steps "
            f"skill in CI mode: read the newest context .md file from this directory on "
            f"disk (there is no chat attachment): {ctx_dir}\n"
            f"Do not stop for human checkpoints. Write a numbered implementation plan, "
            f"including an 'Impacted Files' section, to this EXACT file (its parent "
            f".harness ALREADY EXISTS, do not mkdir, shell is disallowed): {plan_file}\n"
            f"  STORY: {story}\n"
            f"THIS IS A PLANNING PHASE ONLY. You MUST NOT create, edit, or write any "
            f".java file or any source or test file. Do NOT implement the change in this "
            f"phase — implementation happens in a later phase. The ONLY file you are "
            f"permitted to write is {plan_file}. Any attempt to write under src/main or "
            f"src/test will be denied by the harness and will FAIL the run. Describe the "
            f"intended code changes as TEXT inside the plan file instead: list the target "
            f"file paths, method signatures, and (optionally) before/after snippets as "
            f"fenced code blocks within {plan_file}. Do not call any file-write tool for "
            f"anything other than {plan_file}.\n"
            f"Write ONLY {plan_file}."
        ),
        "coding": (
            f"Implement the change described in {plan_file} for:\n  STORY: {story}\n"
            f"Edit ONLY application source under {src_main}/. Do NOT create or edit any test files."
        ),
        "unit_testing": (
            f"Write unit tests under {src_test}/ that verify:\n  STORY: {story}\n"
            f"Do NOT modify application code under {src_main}/. Tests only."
        ),
        "documentation": (
            f"Document the change as a markdown file under {docs_dir}/ (the directory "
            f"ALREADY EXISTS, do not mkdir, shell is disallowed) for:\n  STORY: {story}\n"
            f"Write ONLY under {docs_dir}/."
        ),
        "raise_pr": (
            f"Summarize the change for a pull request body and write it to "
            f"this EXACT file (parent .harness ALREADY EXISTS, shell disallowed): "
            f"{pr_body}\n  STORY: {story}\nWrite ONLY {pr_body}."
        ),
    }[phase.id]

    out = base
    if run.last_feedback and run.approvals.get(phase.id) == "rejected":
        out += f"\n\nThe previous attempt was REJECTED. Address this feedback:\n{run.last_feedback}\n"
    return out


class SdkAgentRunner:
    def __init__(self, model: str = DEFAULT_MODEL, log=print):
        self.model = model
        self.log = log

    def run(self, phase: Phase, prompt: str, run: RunState, repo_root: Path) -> AgentResult:
        """Synchronous wrapper the executor calls; drives the async SDK underneath."""
        try:
            return asyncio.run(self._run_async(phase, run, repo_root))
        except Exception as e:  # surface as SDK_ERROR via the executor
            import traceback
            tb = traceback.format_exc()
            self.log("  ! SDK exception:\n" + tb)
            msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__} (no message)"
            return AgentResult(errored=True, error_msg=msg)

    async def _run_async(self, phase: Phase, run: RunState, repo_root: Path) -> AgentResult:
        import os
        from copilot import CopilotClient
        from copilot.rpc import (
            PermissionDecisionApproveOnce,
            PermissionDecisionReject,
        )

        attempted_writes: list[str] = []

        # ---- THE INTERLOCK (real-time, at the SDK) ----
        def on_permission_request(request, invocation):
            # NOTE: request.kind is a plain string (ClassVar), NOT an enum.
            # Using request.kind.value here would raise AttributeError, which the
            # SDK silently turns into a denial.
            kind = request.kind
            if kind == "write":
                path = getattr(request, "file_name", "") or ""
                attempted_writes.append(path)
                self.log(f"  . write request: {path}")
                if not is_write_allowed(path, phase.allowed_writes, repo_root=str(repo_root)):
                    msg = deny_reason(path, phase.id, phase.allowed_writes, repo_root=str(repo_root))
                    self.log("  ! " + msg)
                    return PermissionDecisionReject(feedback=msg)
                return PermissionDecisionApproveOnce()
            if kind == "shell":
                cmd = getattr(request, "full_command_text", "") or str(getattr(request, "commands", ""))
                self.log(f"  ! shell denied: {cmd}")
                return PermissionDecisionReject(
                    feedback="Shell commands are not permitted in this phase."
                )
            # read / url / memory / etc -> approve for the PoC (tighten later)
            self.log(f"  . {kind} request -> approved")
            return PermissionDecisionApproveOnce()

        # Build the prompt: capability layer (skills/instructions) + phase task.
        capability = _load_capability_layer(repo_root, phase)
        task = _phase_instruction(phase, run, repo_root)
        full_prompt = (capability + "\n\n" if capability else "") + task

        # per-phase model: config phase_models[phase_id] overrides the default model.
        from config import HarnessConfig as _HC
        _cfg = _HC.load(repo_root / ".harness")
        phase_model = (_cfg.model_for_phase(phase.id) if _cfg else None) or self.model
        self.log(f"  [model] phase '{phase.id}' -> {phase_model}")

        # working_directory scopes the agent to the petclinic repo so writes match
        # our globs. use_logged_in_user=True rides on your authed Copilot CLI (Pro).
        # Auth: pass the token EXPLICITLY to the client (the reliable path).
        # Env-var auto-detection doesn't always propagate to the spawned CLI
        # subprocess in CI, so we read it here and hand it to CopilotClient via
        # github_token=. When a token is present, the SDK sets use_logged_in_user
        # to False automatically. Locally (no token), fall back to logged-in user.
        ci_token = (os.environ.get("COPILOT_GITHUB_TOKEN")
                    or os.environ.get("GH_TOKEN")
                    or os.environ.get("GITHUB_TOKEN"))

        client_kwargs = {"working_directory": str(repo_root)}
        if ci_token:
            client_kwargs["github_token"] = ci_token
        else:
            client_kwargs["use_logged_in_user"] = True

        async with CopilotClient(**client_kwargs) as client:
            async with await client.create_session(
                on_permission_request=on_permission_request,
                model=phase_model,
            ) as session:
                done = asyncio.Event()
                last_message = {"text": ""}
                usage = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "reasoning": 0}
                seen_events = {}
                errors = []
                # capability attribution: which skills the SDK loaded (definitive)
                # and which tools it invoked (inferred from tool.execution_start).
                skills_loaded: list[str] = []
                tools_invoked: list[str] = []

                def on_event(event):
                    t = event.type.value
                    # DIAGNOSTIC: count every event type so we can see what the SDK emits in CI
                    seen_events[t] = seen_events.get(t, 0) + 1
                    if t == "assistant.message":
                        try:
                            last_message["text"] = event.data.content or ""
                        except Exception:
                            pass
                    elif t == "assistant.usage":
                        try:
                            d = event.data
                            usage["input"] += getattr(d, "input_tokens", 0) or 0
                            usage["output"] += getattr(d, "output_tokens", 0) or 0
                            usage["cache_read"] += getattr(d, "cache_read_tokens", 0) or 0
                            usage["cache_write"] += getattr(d, "cache_write_tokens", 0) or 0
                            usage["reasoning"] += getattr(d, "reasoning_tokens", 0) or 0
                        except Exception:
                            pass
                    elif "error" in t.lower():
                        # capture any error-type event so failures aren't silent
                        try:
                            errors.append(f"{t}: {getattr(event.data, 'message', str(event.data))[:300]}")
                        except Exception:
                            errors.append(t)
                    elif t == "session.skills_loaded":
                        # DEFINITIVE: the skills the SDK actually loaded this session.
                        try:
                            for n in _extract_names(event.data, "skills", "loaded", "items"):
                                if n not in skills_loaded:
                                    skills_loaded.append(n)
                        except Exception:
                            pass
                    elif t in ("tool.execution_start", "tool.execution_complete"):
                        # INFERRED USE: a skill/tool was invoked. Skills surface as
                        # tool calls, so this is the closest signal to "was used".
                        # Record on _start (the canonical trigger); _complete is a
                        # harmless fallback if _start was missed.
                        try:
                            for n in _extract_names(event.data, "tools", "tool", "items"):
                                if n not in tools_invoked:
                                    tools_invoked.append(n)
                        except Exception:
                            pass
                    # terminal events: idle OR any completion-style event ends the turn
                    if t in ("session.idle", "session.completed", "turn.completed", "session.error"):
                        done.set()

                session.on(on_event)
                await session.send(full_prompt)
                # guard against hanging forever if no terminal event arrives
                try:
                    await asyncio.wait_for(done.wait(), timeout=300)
                except asyncio.TimeoutError:
                    self.log("  [diag] timed out waiting for a terminal event")

                # DIAGNOSTICS — what did the SDK actually emit?
                self.log(f"  [diag] events seen: {seen_events}")
                if errors:
                    for e in errors:
                        self.log(f"  [diag] ERROR EVENT: {e}")

                # CAPABILITY ATTRIBUTION — what loaded vs what was invoked.
                # 'configured' is what config.phase_skills SAID should load this
                # phase; 'loaded' is what the SDK reported loading; 'invoked' is
                # what was actually called. loaded != invoked (loaded only means
                # available to the model).
                try:
                    from config import HarnessConfig as _HC2
                    _cfg2 = _HC2.load(repo_root / ".harness")
                    _configured = list((_cfg2.phase_skills or {}).get(phase.id, [])) if _cfg2 else []
                except Exception:
                    _configured = []
                self.log(f"  [skills] phase '{phase.id}': "
                         f"configured={_configured or '(none)'} | "
                         f"loaded={skills_loaded or '(none reported)'} | "
                         f"invoked={tools_invoked or '(none reported)'}")

                if last_message["text"]:
                    self.log("  [agent] " + last_message["text"][:500])

                # report token usage for this phase
                total = usage["input"] + usage["output"]
                if total > 0:
                    self.log(f"  [tokens] phase '{phase.id}': "
                             f"in={usage['input']} out={usage['output']} "
                             f"cache_r={usage['cache_read']} reasoning={usage['reasoning']}")
                # stash on the result so the orchestrator can aggregate
                self._last_usage = usage
                self._last_skills = skills_loaded
                self._last_tools = tools_invoked

        return AgentResult(attempted_writes=attempted_writes, iterations_used=1,
                           tokens=getattr(self, "_last_usage", {}),
                           skills_loaded=getattr(self, "_last_skills", []),
                           tools_invoked=getattr(self, "_last_tools", []))
