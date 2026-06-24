"""
config.py — externalized harness configuration (read from .harness/config.yaml).

Keeps the test command, working module, and validation scope out of code, matching
the toolkit convention of config-driven behaviour. If config.yaml is absent, sane
defaults for spring-petclinic on Windows are used.
"""
from __future__ import annotations
from dataclasses import dataclass
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
            pre_validation_command=data.get("pre_validation_command", cls.pre_validation_command),
            validation_loopback_phase=data.get("validation_loopback_phase", cls.validation_loopback_phase),
            max_validation_retries=int(data.get("max_validation_retries", cls.max_validation_retries)),
            min_coverage=float(data.get("min_coverage", cls.min_coverage)),
            coverage_command=data.get("coverage_command", cls.coverage_command),
            coverage_csv=data.get("coverage_csv", cls.coverage_csv),
            coverage_metric=data.get("coverage_metric", cls.coverage_metric),
            story_file=data.get("story_file", cls.story_file),
        )

    def resolved_test_command(self) -> str:
        """Build the actual command string, applying the targeted filter if set."""
        if self.test_filter:
            # Maven Surefire targeted run
            return f"{self.test_command} -Dtest={self.test_filter}"
        return self.test_command
