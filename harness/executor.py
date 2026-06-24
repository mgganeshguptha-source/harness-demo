"""
executor.py — the PhaseExecutor that the state machine drives.

This is where the harness's guarantees get ENFORCED around the (probabilistic)
agent runner:

  1. It builds the per-phase prompt (capability layer: your skills/instructions).
  2. It runs the agent via an injected AgentRunner (fake OR real SDK).
  3. The runner reports every file write it attempted; the executor checks each
     against is_write_allowed() for the CURRENT phase. Any out-of-bounds write =>
     BOUNDARY_VIOLATION (the interlock).
  4. It enforces the iteration cap (credit guard).
  5. It checks the phase produced its required artifact => else ARTIFACT_MISSING.

The AgentRunner is a Protocol so Phase 3 uses FakeAgentRunner (no SDK) and Phase 4
swaps in SdkAgentRunner (real Copilot) with NO change to this file or the machine.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from contracts import ExitCode
from phases import Phase
from state import RunState
from boundaries import is_write_allowed, deny_reason


@dataclass
class AgentResult:
    """What a runner reports back after attempting a phase."""
    attempted_writes: list = field(default_factory=list)  # paths it tried to write
    iterations_used: int = 1
    errored: bool = False
    error_msg: str = ""


class AgentRunner(Protocol):
    """Runs one phase's work. Fake or real SDK both satisfy this."""
    def run(self, phase: Phase, prompt: str, run: RunState, repo_root: Path) -> AgentResult: ...


class PhaseExecutor:
    def __init__(self, runner: AgentRunner, repo_root: Path, harness_dir: Path, log=print):
        self.runner = runner
        self.repo_root = repo_root
        self.harness_dir = harness_dir
        self.log = log

    def _build_prompt(self, phase: Phase, run: RunState) -> str:
        """Capability layer. In Phase 4 this pulls in .github/skills + instructions.
        For now, a phase-specific instruction string + any rejection feedback."""
        base = f"[{phase.id}] {phase.title}\nUser story: {run.story}\n"
        if run.last_feedback and run.approvals.get(phase.id) == "rejected":
            base += f"\nPrevious attempt was REJECTED. Address this feedback:\n{run.last_feedback}\n"
        return base

    def run_phase(self, phase: Phase, run: RunState) -> ExitCode:
        # --- iteration cap (credit guard) ---
        used = run.iterations.get(phase.id, 0)
        if used >= phase.max_iterations:
            self.log(f"  ! iteration cap {phase.max_iterations} reached for {phase.id}")
            return ExitCode.ITERATION_CAP

        prompt = self._build_prompt(phase, run)

        # Deterministic setup: ensure declared dirs exist so the agent never needs
        # shell to mkdir. These are within the phase's allowed_writes by construction.
        for d in getattr(phase, "pre_create_dirs", ()):
            target = self.repo_root / d
            try:
                target.mkdir(parents=True, exist_ok=True)
                self.log(f"  [harness] ensured dir exists: {d}/")
            except Exception as e:
                self.log(f"  [harness] could not create dir {d}: {e}")

        result = self.runner.run(phase, prompt, run, self.repo_root)

        run.iterations[phase.id] = used + result.iterations_used

        if result.errored:
            self.log(f"  ! runner error: {result.error_msg}")
            return ExitCode.SDK_ERROR

        # --- THE INTERLOCK: every attempted write must be in-bounds ---
        for w in result.attempted_writes:
            if not is_write_allowed(w, phase.allowed_writes, repo_root=str(self.repo_root)):
                self.log("  ! " + deny_reason(w, phase.id, phase.allowed_writes, repo_root=str(self.repo_root)))
                return ExitCode.BOUNDARY_VIOLATION

        # --- pinned artifact must exist ---
        if phase.required_artifact:
            artifact = self.repo_root / phase.required_artifact
            if not artifact.exists():
                self.log(f"  ! required artifact missing: {phase.required_artifact}")
                return ExitCode.ARTIFACT_MISSING

        return ExitCode.OK
