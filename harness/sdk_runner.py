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


def _load_capability_layer(repo_root: Path, phase: Phase) -> str:
    """Pull in .github/skills + .github/instructions as the capability layer.

    Best-effort: if the files don't exist, we proceed with the base prompt.
    We keep this simple — concatenate any instruction markdown relevant to the
    phase. Your existing toolkit files slot in here unchanged.
    """
    chunks = []
    gh = repo_root / ".github"
    for sub in ("instructions", "skills"):
        d = gh / sub
        if d.is_dir():
            for md in sorted(d.rglob("*.md")):
                try:
                    chunks.append(f"\n--- {sub}/{md.name} ---\n" + md.read_text(encoding="utf-8"))
                except Exception:
                    pass
    return "\n".join(chunks)


def _phase_instruction(phase: Phase, run: RunState, repo_root: Path) -> str:
    """The per-phase task prompt. Phase-specific, story-aware, feedback-aware."""
    story = run.story
    base = {
        "context": (
            f"Explore the repository (read-only) and write a concise context document "
            f"to .harness/context.md describing exactly which files must change to implement:\n"
            f"  STORY: {story}\n"
            f"Do NOT modify any source files in this phase. Only write .harness/context.md."
        ),
        "prompt_steps": (
            f"Based on .harness/context.md, write a numbered implementation plan to "
            f".harness/prompt-steps.md for:\n  STORY: {story}\n"
            f"Include an 'Impacted Files' section. Only write .harness/prompt-steps.md."
        ),
        "coding": (
            f"Implement the change described in .harness/prompt-steps.md for:\n  STORY: {story}\n"
            f"Edit ONLY application source under src/main/. Do NOT create or edit any test files."
        ),
        "unit_testing": (
            f"Write unit tests under src/test/ that verify:\n  STORY: {story}\n"
            f"Do NOT modify application code under src/main/. Tests only."
        ),
        "documentation": (
            f"Document the change under docs/ for:\n  STORY: {story}\nOnly write under docs/."
        ),
        "raise_pr": (
            f"Summarize the change for a pull request body and write it to "
            f".harness/pr-body.md for:\n  STORY: {story}\nOnly write .harness/pr-body.md."
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

        # Auth mode: in CI a Copilot token env var is set (COPILOT_GITHUB_TOKEN /
        # GH_TOKEN / GITHUB_TOKEN). When present, do NOT use stored login — the SDK
        # picks up the token automatically. Locally (no token), use the logged-in
        # user (your interactive Copilot CLI session).
        has_ci_token = bool(
            os.environ.get("COPILOT_GITHUB_TOKEN")
            or os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
        )
        use_logged_in = not has_ci_token

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

        # working_directory scopes the agent to the petclinic repo so writes match
        # our globs. use_logged_in_user=True rides on your authed Copilot CLI (Pro).
        async with CopilotClient(
            working_directory=str(repo_root),
            use_logged_in_user=use_logged_in,
        ) as client:
            async with await client.create_session(
                on_permission_request=on_permission_request,
                model=self.model,
            ) as session:
                done = asyncio.Event()
                last_message = {"text": ""}

                def on_event(event):
                    t = event.type.value
                    if t == "assistant.message":
                        try:
                            last_message["text"] = event.data.content or ""
                        except Exception:
                            pass
                    elif t == "session.idle":
                        done.set()

                session.on(on_event)
                await session.send(full_prompt)
                await done.wait()

                if last_message["text"]:
                    self.log("  [agent] " + last_message["text"][:500])

        return AgentResult(attempted_writes=attempted_writes, iterations_used=1)
