"""
phases.py — the 10-phase spine of the harness.

Each Phase declares, DECLARATIVELY:
  - name
  - whether it runs the model (probabilistic) or is a pure gate
  - allowed write globs   -> the interlock the permission handler enforces
  - required artifact      -> the pinned output that must exist to advance
  - human_gate             -> whether a human approve/reject follows

The sequence here is the single source of truth. The state machine walks this
list; it cannot skip, reorder, or jump. That is the "sequence lives in code"
guarantee from the harness thesis.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class PhaseKind(Enum):
    MODEL = auto()   # spawns a Copilot session to do fuzzy work
    GATE = auto()    # pure human checkpoint, no model call


@dataclass(frozen=True)
class Phase:
    id: str
    title: str
    kind: PhaseKind
    # Write boundary: glob patterns the model MAY write to during this phase.
    # Empty list = no file writes allowed at all (read-only phase).
    # The permission handler denies any write whose path matches none of these.
    allowed_writes: tuple = field(default_factory=tuple)
    # Artifact that must exist (relative to repo root) for the phase to return OK.
    required_artifact: Optional[str] = None
    # Does a human approve/reject gate follow this phase?
    human_gate: bool = False
    # Per-phase iteration budget (model turns) — the credit guard.
    max_iterations: int = 6
    # If True, the HARNESS runs the validation gate (mvn test) after this phase
    # returns OK. Non-zero exit => VALIDATION_FAILED => halt before advancing.
    validate_after: bool = False
    # Directories (repo-relative) the HARNESS ensures exist before the phase runs.
    # Deterministic setup so the agent never needs shell to mkdir. These dirs must
    # fall within the phase's allowed_writes.
    pre_create_dirs: tuple = field(default_factory=tuple)


# ---- THE SPINE ----------------------------------------------------------
# .harness/ is the machine-local workspace (gitignored).
# src/main/** and src/test/** are the petclinic app under change.

PHASES = (
    Phase(
        id="context",
        title="Story -> Context building",
        kind=PhaseKind.MODEL,
        allowed_writes=(".harness/**",),          # may ONLY write workspace files
        required_artifact=".harness/context.md",
        human_gate=True,                            # -> review context
        max_iterations=6,
    ),
    Phase(
        id="prompt_steps",
        title="Prompt steps (implementation plan)",
        kind=PhaseKind.MODEL,
        allowed_writes=(".harness/**",),
        required_artifact=".harness/prompt-steps.md",
        human_gate=True,                            # -> review steps
        max_iterations=6,
    ),
    Phase(
        id="coding",
        title="Coding (main source only)",
        kind=PhaseKind.MODEL,
        # THE KEY INTERLOCK: may write app code, but NOT tests.
        allowed_writes=("src/main/**", ".harness/**"),
        required_artifact=None,
        human_gate=True,                            # -> review code
        max_iterations=10,
    ),
    Phase(
        id="unit_testing",
        title="Unit testing (test source only)",
        kind=PhaseKind.MODEL,
        # THE MIRROR INTERLOCK: may write tests, but main is now FROZEN
        # (can't quietly edit code to make tests pass).
        allowed_writes=("src/test/**", ".harness/**"),
        required_artifact=None,
        human_gate=False,                           # validation gate follows instead
        max_iterations=10,
        validate_after=True,                        # harness runs mvn test here
    ),
    Phase(
        id="documentation",
        title="Create documentation",
        kind=PhaseKind.MODEL,
        allowed_writes=("docs/**", ".harness/**"),
        required_artifact=None,
        human_gate=True,                            # -> review docs
        max_iterations=6,
        pre_create_dirs=("docs",),                  # harness makes docs/ so agent needn't shell
    ),
    Phase(
        id="raise_pr",
        title="Raise PR request",
        kind=PhaseKind.MODEL,
        allowed_writes=(".harness/**",),
        required_artifact=None,
        human_gate=False,
        max_iterations=4,
    ),
)


def phase_by_id(pid: str) -> Phase:
    for p in PHASES:
        if p.id == pid:
            return p
    raise KeyError(pid)


def next_phase(pid: str) -> Optional[Phase]:
    ids = [p.id for p in PHASES]
    i = ids.index(pid)
    return PHASES[i + 1] if i + 1 < len(PHASES) else None
