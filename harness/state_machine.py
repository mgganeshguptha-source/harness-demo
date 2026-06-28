"""
state_machine.py — the deterministic engine.

It walks PHASES in order. For each phase it asks a PhaseExecutor to run the phase
and return an ExitCode. The machine NEVER advances on the model's say-so; it advances
only on ExitCode.OK. Every other code maps to a specific, non-negotiable transition:

    OK                 -> record completion; if human_gate, pause for approval; else advance
    AWAITING_APPROVAL  -> pause (handled via OK + human_gate, kept for explicit executors)
    REJECTED           -> stay on the same phase, carry feedback back in
    BOUNDARY_VIOLATION -> HALT (an interlock tripped — the whole point)
    ITERATION_CAP      -> HALT (credit guard)
    VALIDATION_FAILED  -> HALT (e.g. mvn test red)
    ARTIFACT_MISSING   -> HALT (phase didn't produce its pinned output)
    SDK_ERROR / CONFIG_ERROR -> HALT

The executor is injected (dependency injection), so this engine is testable with a
fake executor — zero SDK, zero credits. That is the claude-shepherd AgentRunner seam,
one layer up.
"""
from __future__ import annotations
from pathlib import Path
from typing import Protocol

from contracts import ExitCode, label
from phases import PHASES, Phase, next_phase
from state import RunState


class PhaseExecutor(Protocol):
    """Anything that can run a phase and return an ExitCode.

    In Phase 3 we implement FakeExecutor (no SDK). In Phase 4, SdkExecutor (real Copilot).
    The state machine doesn't know or care which it's given.
    """
    def run_phase(self, phase: Phase, run: RunState) -> ExitCode: ...


# Codes that mean "stop the machine and surface to a human/operator"
_HALTING = {
    ExitCode.BOUNDARY_VIOLATION,
    ExitCode.ITERATION_CAP,
    ExitCode.VALIDATION_FAILED,
    ExitCode.ARTIFACT_MISSING,
    ExitCode.SDK_ERROR,
    ExitCode.CONFIG_ERROR,
}


class StateMachine:
    def __init__(self, executor: PhaseExecutor, harness_dir: Path, repo_root: Path = None,
                 log=print, validator=None):
        self.executor = executor
        self.harness_dir = harness_dir
        # repo_root is where the validation gate runs mvn; fall back to executor's.
        self.repo_root = repo_root or getattr(executor, "repo_root", harness_dir.parent)
        self.log = log
        # validator(repo_root, harness_dir, log) -> object with .passed/.summary/.exit_code/.output_tail
        # Defaults to the real mvn-test gate; tests inject a fake to avoid shelling out.
        self._validator = validator

    def _phase(self, pid: str) -> Phase:
        for p in PHASES:
            if p.id == pid:
                return p
        raise KeyError(pid)

    def step(self, run: RunState) -> RunState:
        """Execute exactly ONE phase and apply the resulting transition.

        Returns the updated RunState. Caller loops `step` until status is
        'done', 'halted', or 'awaiting_approval'.
        """
        phase = self._phase(run.current_phase)
        self.log(f"\n=== Phase '{phase.id}' : {phase.title} ===")

        code = self.executor.run_phase(phase, run)
        self.log(f"--> exit {int(code)} ({label(code)})")

        # ---- apply the transition ----
        if code in _HALTING:
            run.status = "halted"
            run.save(self.harness_dir)
            return run

        if code == ExitCode.REJECTED:
            # stay put; feedback already recorded on run by the gate
            run.approvals[phase.id] = "rejected"
            run.status = "running"
            run.save(self.harness_dir)
            return run

        if code in (ExitCode.OK, ExitCode.AWAITING_APPROVAL):
            if phase.id not in run.completed_phases:
                run.completed_phases.append(phase.id)

            # ---- CLARIFICATION GATE ----
            # After the context phase, scan for [NEEDS CLARIFICATION] markers.
            # Any remaining => the story is ambiguous => halt for human input,
            # do NOT proceed to prompt_steps.
            if getattr(phase, "scan_clarifications", False):
                from clarification import scan_clarifications as _scan
                from config import HarnessConfig as _HC
                _cfg = _HC.load(self.harness_dir)
                cr = _scan(self.repo_root, _cfg.context_output_dir)
                if not cr.clear:
                    self.log(f"  ! NEEDS_CLARIFICATION — {len(cr.items)} item(s) unresolved in {cr.scanned_file}")
                    for it in cr.items:
                        self.log("      • " + it)
                    run.status = "needs_input"
                    run.save(self.harness_dir)
                    return run
                self.log("  [harness] clarification gate: clear (no open items)")

            # ---- DETERMINISTIC VALIDATION GATE ----
            # The harness (not the agent) runs the tests. Red => halt before advancing.
            if phase.validate_after:
                if self._validator is not None:
                    vr = self._validator(self.repo_root, self.harness_dir, self.log)
                else:
                    from validation import run_validation
                    vr = run_validation(self.repo_root, self.harness_dir, log=self.log)
                self.log(f"  [harness] validation: {vr.summary} (exit {vr.exit_code})")
                if not vr.passed:
                    from config import HarnessConfig
                    cfg = HarnessConfig.load(self.harness_dir)
                    run.validation_attempts += 1

                    loopback = cfg.validation_loopback_phase
                    if loopback and run.validation_attempts <= cfg.max_validation_retries:
                        # CONDITIONAL TRANSITION (known edge, not dynamic):
                        # tests red -> go back to the coding phase carrying the failure
                        # as feedback, and let it fix + re-validate.
                        self.log(f"  ! VALIDATION_FAILED — looping back to '{loopback}' "
                                 f"(attempt {run.validation_attempts}/{cfg.max_validation_retries})")
                        run.last_feedback = (
                            "The test build FAILED. Fix the production code so tests pass. "
                            "Do not edit tests. Failure output:\n" + vr.output_tail
                        )
                        # reset iteration budget for the loopback phase so it can act
                        run.iterations[loopback] = 0
                        run.approvals[loopback] = "rejected"  # forces re-run semantics
                        run.current_phase = loopback
                        run.status = "running"
                        run.save(self.harness_dir)
                        return run

                    # retries exhausted (or loopback disabled) -> halt for a human
                    self.log(f"  ! VALIDATION_FAILED — retries exhausted "
                             f"({run.validation_attempts-1}/{cfg.max_validation_retries}); halting")
                    self.log("  --- test output tail ---\n" + vr.output_tail)
                    run.status = "halted"
                    run.save(self.harness_dir)
                    return run

            if phase.human_gate and run.approvals.get(phase.id) != "approved":
                # pause for the human; resolve_gate() resumes us
                run.status = "awaiting_approval"
                run.save(self.harness_dir)
                return run

            # advance
            nxt = next_phase(phase.id)
            if nxt is None:
                run.status = "done"
            else:
                run.current_phase = nxt.id
                run.status = "running"
            run.save(self.harness_dir)
            return run

        # unknown code — fail safe by halting
        run.status = "halted"
        run.save(self.harness_dir)
        return run

    def resolve_gate(self, run: RunState, approved: bool, feedback: str = "") -> RunState:
        """Apply a human decision to a phase that is awaiting approval."""
        phase = self._phase(run.current_phase)
        if run.status != "awaiting_approval":
            raise RuntimeError(f"Phase '{phase.id}' is not awaiting approval")

        if approved:
            run.approvals[phase.id] = "approved"
            run.last_feedback = None
            # stamp the execution record with the human's approval (coding phase)
            if getattr(phase, "record_execution", False):
                try:
                    from execution_record import stamp_approval
                    stamp_approval(self.harness_dir / "prompt-steps.md", True)
                except Exception:
                    pass
            nxt = next_phase(phase.id)
            if nxt is None:
                run.status = "done"
            else:
                run.current_phase = nxt.id
                run.status = "running"
        else:
            run.approvals[phase.id] = "rejected"
            run.last_feedback = feedback
            if getattr(phase, "record_execution", False):
                try:
                    from execution_record import stamp_approval
                    stamp_approval(self.harness_dir / "prompt-steps.md", False, feedback)
                except Exception:
                    pass
            run.status = "running"   # re-run the same phase with feedback
        run.save(self.harness_dir)
        return run

    def run_until_pause(self, run: RunState, max_steps: int = 50) -> RunState:
        """Drive steps until the machine needs a human or finishes (or safety cap)."""
        steps = 0
        while run.status == "running" and steps < max_steps:
            run = self.step(run)
            steps += 1
        return run
