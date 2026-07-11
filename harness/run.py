"""
run.py — the harness CLI.

Usage:
  python run.py init   --repo <path> --feature PC-1-fullname --story "Add getFullName() to Owner"
  python run.py run    --repo <path>            # drive until a gate or completion
  python run.py approve --repo <path>           # approve current gate, continue
  python run.py reject  --repo <path> --feedback "..."   # reject, re-run phase
  python run.py status --repo <path>

Phase 3: uses FakeAgentRunner (no SDK, no credits). Add --misbehave <phase_id> to
watch the interlock halt the run on an out-of-bounds write.

Phase 4 will add  --real  to swap in the Copilot SDK runner.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from state import RunState
from state_machine import StateMachine
from executor import PhaseExecutor
from fake_runner import FakeAgentRunner


def _harness_dir(repo: Path) -> Path:
    return repo / ".harness"


def _build_machine(repo: Path, misbehave: str | None = None,
                   real: bool = False, model: str | None = None) -> StateMachine:
    if real:
        from sdk_runner import SdkAgentRunner, DEFAULT_MODEL
        runner = SdkAgentRunner(model=model or DEFAULT_MODEL)
    else:
        runner = FakeAgentRunner(misbehave_in=misbehave)
    executor = PhaseExecutor(runner, repo_root=repo, harness_dir=_harness_dir(repo))
    return StateMachine(executor, harness_dir=_harness_dir(repo))


def cmd_init(args):
    repo = Path(args.repo).resolve()
    hd = _harness_dir(repo)
    hd.mkdir(parents=True, exist_ok=True)
    from phases import PHASES

    # Story precedence: explicit --story flag, else read from the configured file
    # (which in production an MCP/Jira step would populate).
    story = getattr(args, "story", None)
    if not story:
        from config import HarnessConfig
        from story_source import FileStorySource
        cfg = HarnessConfig.load(hd)
        src = FileStorySource(repo / cfg.story_file)
        story = src.get_story()
        print(f"Read story from {cfg.story_file}")

    run = RunState(feature_id=args.feature, story=story, current_phase=PHASES[0].id)
    run.save(hd)
    print(f"Initialized run for '{args.feature}' at {hd}")
    print(f"First phase: {run.current_phase}")


def _load(repo: Path) -> RunState:
    run = RunState.load(_harness_dir(repo))
    if run is None:
        print("No run found. Run `init` first.")
        sys.exit(2)
    return run


def cmd_run(args):
    repo = Path(args.repo).resolve()
    run = _load(repo)
    sm = _build_machine(repo, misbehave=args.misbehave,
                        real=getattr(args, "real", False), model=getattr(args, "model", None))
    run = sm.run_until_pause(run)
    _report(run)


def cmd_autorun(args):
    """CI driver: run all phases end to end, auto-approving human gates.
    The deterministic guarantees (boundaries, validation, coverage, retry cap)
    still fully apply — only the *human* approval is automated here."""
    repo = Path(args.repo).resolve()
    run = _load(repo)
    sm = _build_machine(repo, real=True, model=getattr(args, "model", None))
    max_cycles = 50
    for _ in range(max_cycles):
        run = sm.run_until_pause(run)
        if run.status == "awaiting_approval":
            print(f"  [auto-approve] gate: {run.current_phase}")
            run = sm.resolve_gate(run, approved=True)
        elif run.status in ("done", "halted", "needs_input"):
            break
    _report(run)
    # exit non-zero if the harness halted or needs human input (CI job fails visibly)
    if run.status in ("halted", "needs_input"):
        import sys as _sys
        _sys.exit(1)


def cmd_approve(args):
    repo = Path(args.repo).resolve()
    run = _load(repo)
    sm = _build_machine(repo)  # no execution here; runner choice irrelevant
    if run.status != "awaiting_approval":
        print(f"Nothing to approve (status: {run.status})")
        return
    run = sm.resolve_gate(run, approved=True)
    print(f"Approved. Advanced to: {run.current_phase} ({run.status})")
    print(f">>> Execute it with:  python run.py run --repo {args.repo} --real --model <model>")


def cmd_reject(args):
    repo = Path(args.repo).resolve()
    run = _load(repo)
    sm = _build_machine(repo)
    if run.status != "awaiting_approval":
        print(f"Nothing to reject (status: {run.status})")
        return
    run = sm.resolve_gate(run, approved=False, feedback=args.feedback or "")
    print(f"Rejected '{run.current_phase}'. It will re-run with your feedback on next `run`.")


def _run_id() -> str:
    """A unique-per-run identifier for the audit subfolder. In CI, GitHub's
    run id is stable and collision-free; locally we fall back to a UTC
    timestamp. This makes audit/<feature>/<run_id>/ unique per run so context,
    run-summary, and every other artifact are retained rather than overwritten."""
    import os
    from datetime import datetime, timezone
    rid = os.environ.get("GITHUB_RUN_ID")
    if rid:
        attempt = os.environ.get("GITHUB_RUN_ATTEMPT")
        return f"{rid}-{attempt}" if attempt and attempt != "1" else rid
    return datetime.now(timezone.utc).strftime("run-%Y%m%d-%H%M%S")


def cmd_collect_audit(args):
    """Collect the run's audit artifacts into audit/<feature>/<run_id>/ for
    permanent retention in the repo. Gathers: the context file(s), prompt-steps.md
    (which includes the appended EXECUTION RECORD), validation-report.txt,
    pr-body.md, and a run-summary with token/cost totals. The PR step then commits
    this folder. Each run writes to its OWN run_id subfolder, so re-running the
    same feature never overwrites a prior run's trail."""
    import shutil, json
    repo = Path(args.repo).resolve()
    run = _load(repo)
    feature = run.feature_id
    run_id = _run_id()
    audit_dir = repo / "audit" / feature / run_id
    audit_dir.mkdir(parents=True, exist_ok=True)

    hd = _harness_dir(repo)
    ctx_dir = repo / ".github" / "story-context-files"

    copied = []
    # newest context file (the agent may write a timestamped name)
    if ctx_dir.is_dir():
        ctxs = sorted(ctx_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if ctxs:
            dst = audit_dir / "context.md"
            shutil.copy2(ctxs[0], dst); copied.append("context.md")
    # planning + audit files from the workspace
    for name in ("prompt-steps.md", "review.md", "validation-report.txt",
                 "pr-body.md", "capability-manifest.json"):
        src = hd / name
        if src.exists():
            shutil.copy2(src, audit_dir / name); copied.append(name)

    # a machine-readable run summary (tokens, cost, phases, status)
    summary = {
        "feature": feature,
        "run_id": run_id,
        "status": run.status,
        "completed_phases": run.completed_phases,
        "total_tokens": run.total_tokens,
        "phase_token_log": run.phase_token_log,
    }
    (audit_dir / "run-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    copied.append("run-summary.json")

    print(f"Collected audit trail into audit/{feature}/{run_id}/:")
    for c in copied:
        print(f"  - {c}")


def cmd_status(args):
    repo = Path(args.repo).resolve()
    run = _load(repo)
    _report(run)


def _report(run: RunState):
    print("\n--- HARNESS STATUS ---")
    print(f"feature : {run.feature_id}")
    print(f"phase   : {run.current_phase}")
    print(f"status  : {run.status}")
    print(f"done    : {run.completed_phases}")

    # per-phase token breakdown with running totals + cost estimate
    if run.phase_token_log:
        print("\n  token usage & estimated cost by phase:")
        total_credits = 0.0
        any_unknown = False
        for e in run.phase_token_log:
            model = f"[{e.get('model','')}]"
            if e.get("included"):
                cost = "included (0 cr)"
            elif e.get("est_credits") is not None:
                cost = f"~{e['est_credits']:.1f} cr (~${e['est_usd']:.4f})"
                total_credits += e["est_credits"]
            else:
                cost = "rate unknown"; any_unknown = True
            print(f"    {e['phase']:<14}{model:<22} "
                  f"{e['phase_tokens']:>7} tok   {cost}")
        approx = "≈" if not any_unknown else "≳"
        print(f"\n  estimated run cost: {approx} {total_credits:.1f} AI credits "
              f"(≈ ${total_credits * 0.01:.4f})   [1 credit = $0.01]")
        print(f"  NOTE: estimate only — included models cost 0; confirm the actual")
        print(f"        charge via GitHub Billing (before/after credit delta).")

    # token + rough credit estimate (1 credit = $0.01; tokens priced per-model,
    # so this is an INDICATIVE total, not the billed amount — confirm in GitHub billing)
    tk = run.total_tokens or {}
    tin, tout = tk.get("input", 0), tk.get("output", 0)
    if tin or tout:
        print(f"\n  totals: input={tin} output={tout} "
              f"cache_read={tk.get('cache_read', 0)} reasoning={tk.get('reasoning', 0)}")
        print(f"          total billable tokens (in+out) = {tin + tout}")
        print(f"          (see GitHub Billing for the exact AI-credit charge)")

    if run.status == "awaiting_approval":
        print(f"\n>>> Phase '{run.current_phase}' awaits your review.")
        print(">>> Run:  python run.py approve --repo <path>")
        print(">>>   or: python run.py reject  --repo <path> --feedback \"...\"")
    elif run.status == "halted":
        print("\n>>> HALTED by an interlock. Inspect the log above for the reason.")
    elif run.status == "needs_input":
        print("\n>>> NEEDS INPUT: the context has unresolved [NEEDS CLARIFICATION] items.")
        print(">>> Resolve them in the story, then re-run from the context phase.")
    elif run.status == "done":
        print("\n>>> All phases complete.")


def main():
    p = argparse.ArgumentParser(prog="harness")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init"); pi.add_argument("--repo", required=True)
    pi.add_argument("--feature", required=True)
    pi.add_argument("--story", default=None, help="story text; if omitted, read from config.story_file")
    pi.set_defaults(func=cmd_init)

    pr = sub.add_parser("run"); pr.add_argument("--repo", required=True)
    pr.add_argument("--misbehave", default=None, help="phase id to inject an out-of-bounds write")
    pr.add_argument("--real", action="store_true", help="use the live Copilot SDK (spends credits)")
    pr.add_argument("--model", default=None, help="override the model string")
    pr.set_defaults(func=cmd_run)

    pa = sub.add_parser("approve"); pa.add_argument("--repo", required=True)
    pa.add_argument("--misbehave", default=None, help="phase id to inject an out-of-bounds write on the auto-continued phase")
    pa.add_argument("--real", action="store_true", help="use the live Copilot SDK (spends credits)")
    pa.add_argument("--model", default=None, help="override the model string")
    pa.set_defaults(func=cmd_approve)

    prj = sub.add_parser("reject"); prj.add_argument("--repo", required=True)
    prj.add_argument("--feedback", default=""); prj.set_defaults(func=cmd_reject)

    ps = sub.add_parser("status"); ps.add_argument("--repo", required=True)
    ps.set_defaults(func=cmd_status)

    par = sub.add_parser("autorun"); par.add_argument("--repo", required=True)
    par.add_argument("--model", default=None, help="override the model string")
    par.set_defaults(func=cmd_autorun)

    pca = sub.add_parser("collect-audit"); pca.add_argument("--repo", required=True)
    pca.set_defaults(func=cmd_collect_audit)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
