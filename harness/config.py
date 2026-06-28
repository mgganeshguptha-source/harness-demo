"""
config.py — externalized harness configuration (read from .harness/config.yaml).

Keeps the test command, working module, and validation scope out of code, matching
the toolkit convention of config-driven behaviour. If config.yaml is absent, sane
defaults for spring-petclinic on Windows are used.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml  # pyyaml
except Exception:
    yaml = None


@dataclass
class HarnessConfig:
    # Command to run tests. {test_filter} is substituted (or removed) at runtime.
    # On Windows petclinic ships mvnw.cmd; on *nix it's ./mvnw.
    test_command: str = "mvnw.cmd test"
    # Optional targeted filter for a fast loop. Empty => full suite.
    test_filter: str = "OwnerTest"
    # Seconds before the test run is killed (guards a hung build).
    test_timeout: int = 600
    # Default model for live runs.
    model: str = "gpt-5-mini"
    # Per-phase model override. A phase uses phase_models[phase_id] if present,
    # else falls back to `model`. Put cheap models on simple phases, stronger
    # models on coding/testing.
    phase_models: dict = field(default_factory=dict)
    # Deterministic normalization run by the HARNESS before validation.
    # spring-javaformat:apply rewrites files to the project's required format.
    # Empty string => skip. This is a fixed, known goal — not arbitrary execution.
    pre_validation_command: str = "mvnw.cmd spring-javaformat:apply"
    # When validation fails, loop back to this phase to fix the code, carrying the
    # failure as feedback. Empty string => don't loop, just halt.
    validation_loopback_phase: str = "coding"
    # Max code<->test cycles before giving up and halting for a human.
    # Guards against infinite loops burning credits.
    max_validation_retries: int = 3
    # --- coverage gate ---
    # If > 0, the harness checks line coverage after tests and fails validation
    # when coverage is below this percent. 0 => coverage gate disabled.
    min_coverage: float = 0.0
    # Goal that produces the JaCoCo CSV. report binds to prepare-package, so we
    # explicitly invoke jacoco:report after tests. Scoped to the filter if set.
    coverage_command: str = "mvnw.cmd jacoco:report"
    # Where JaCoCo writes the CSV (repo-relative).
    coverage_csv: str = "target/site/jacoco/jacoco.csv"
    # Which metric to gate on: LINE, BRANCH, INSTRUCTION, METHOD.
    coverage_metric: str = "LINE"
    # Where the harness reads the user story from (repo-relative). In production an
    # MCP/Jira step writes this file; for the demo it's committed to the repo.
    story_file: str = "stories/current-story.md"
    # Directory the clarification gate scans for the newest context file.
    context_output_dir: str = ".github/story-context-files"
    # ---- selective capability loading ----
    # Master switch: if False, fall back to loading ALL capability files every phase.
    selective_capability: bool = True
    # Which stacks this repo contains. Instruction subfolders NOT in this list are
    # excluded entirely (e.g. a backend-only repo skips angular-frontend/ and
    # mobile-frontend/). Values match the instruction subfolder names. Files
    # directly under instructions/ (not in a stack subfolder) are always considered
    # (these are the cross-cutting guardrails like hipaa, logging-standards).
    # Set to [] or ["*"] to include all stacks.
    repo_stacks: list = field(default_factory=lambda: ["backend"])
    # Glob(s) representing the files each phase is concerned with. An instruction
    # file loads in a phase if its `applyTo` glob intersects the phase's scope.
    # applyTo "**" files are always-on guardrails (load in every phase).
    # Keyed by phase id.
    phase_file_scope: dict = field(default_factory=lambda: {
        "context":      ["src/main/java/**", "src/main/**"],
        "prompt_steps": ["src/main/java/**", "src/main/**"],
        "coding":       ["src/main/java/**"],
        "unit_testing": ["src/test/java/**"],
        "documentation": ["docs/**"],
        "raise_pr":     [],
    })
    # Which named skills (folder names under .github/skills) load in which phase.
    # Skills have no path scope, so this mapping is explicit.
    phase_skills: dict = field(default_factory=lambda: {
        "context":      ["build-context", "analyze-service"],
        "prompt_steps": ["build-prompt-steps"],
        "coding":       ["security-review"],
        "unit_testing": [],
        "documentation": [],
        "raise_pr":     [],
    })

    @classmethod
    def load(cls, harness_dir: Path) -> "HarnessConfig":
        p = harness_dir / "config.yaml"
        if not p.exists() or yaml is None:
            return cls()
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            return cls()
        return cls(
            test_command=data.get("test_command", cls.test_command),
            test_filter=data.get("test_filter", cls.test_filter),
            test_timeout=int(data.get("test_timeout", cls.test_timeout)),
            model=data.get("model", cls.model),
            phase_models=data.get("phase_models") or {},
            pre_validation_command=data.get("pre_validation_command", cls.pre_validation_command),
            validation_loopback_phase=data.get("validation_loopback_phase", cls.validation_loopback_phase),
            max_validation_retries=int(data.get("max_validation_retries", cls.max_validation_retries)),
            min_coverage=float(data.get("min_coverage", cls.min_coverage)),
            coverage_command=data.get("coverage_command", cls.coverage_command),
            coverage_csv=data.get("coverage_csv", cls.coverage_csv),
            coverage_metric=data.get("coverage_metric", cls.coverage_metric),
            story_file=data.get("story_file", cls.story_file),
            context_output_dir=data.get("context_output_dir", cls.context_output_dir),
            selective_capability=bool(data.get("selective_capability", cls.selective_capability)),
            repo_stacks=data.get("repo_stacks") if data.get("repo_stacks") is not None else cls().repo_stacks,
            phase_file_scope=data.get("phase_file_scope") or cls().phase_file_scope,
            phase_skills=data.get("phase_skills") or cls().phase_skills,
        )

    def model_for_phase(self, phase_id: str) -> str:
        """Model for a phase: phase_models[phase_id] if set, else the default."""
        return (self.phase_models or {}).get(phase_id, self.model)

    def resolved_test_command(self) -> str:
        """Build the actual command string, applying the targeted filter if set."""
        if self.test_filter:
            # Maven Surefire targeted run
            return f"{self.test_command} -Dtest={self.test_filter}"
        return self.test_command
