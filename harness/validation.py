"""
validation.py — the deterministic validation gate.

THE HARNESS runs the tests, not the agent. After the unit_testing phase, the state
machine calls run_validation(); it shells out to the configured test command FROM
THE HARNESS (this is allowed — it's our trusted code, not the model), captures the
exit code, and returns pass/fail. A non-zero exit => VALIDATION_FAILED => the run
HALTS before documentation/PR.

This is the interlock that makes "you cannot ship red tests" a guarantee rather
than a hope: the green run is verified by code, as a precondition to proceeding.
"""
from __future__ import annotations
import subprocess
from dataclasses import dataclass
from pathlib import Path

from config import HarnessConfig


@dataclass
class ValidationResult:
    passed: bool
    exit_code: int
    summary: str
    output_tail: str


def _parse_coverage(csv_path: Path, metric: str) -> float | None:
    """Compute percent coverage for the given metric from a JaCoCo CSV.

    Returns None if the file is missing/unparseable. Percent = covered/(covered+missed)
    summed across all rows.
    """
    if not csv_path.exists():
        return None
    try:
        import csv as _csv
        covered = missed = 0
        with csv_path.open(encoding="utf-8") as f:
            for row in _csv.DictReader(f):
                missed += int(row[f"{metric}_MISSED"])
                covered += int(row[f"{metric}_COVERED"])
        total = covered + missed
        if total == 0:
            return None
        return 100.0 * covered / total
    except Exception:
        return None


def run_validation(repo_root: Path, harness_dir: Path, log=print) -> ValidationResult:
    cfg = HarnessConfig.load(harness_dir)

    # ---- DETERMINISTIC PRE-STEP: normalize formatting ----
    # The harness applies the project's required format (spring-javaformat) before
    # validating. This is a fixed, known goal run by trusted harness code — not the
    # agent, and not arbitrary execution. It turns a mechanical "format violation"
    # into a non-issue so validation tests true correctness, not whitespace.
    if cfg.pre_validation_command:
        log(f"  [harness] formatting: {cfg.pre_validation_command}")
        try:
            fmt = subprocess.run(
                cfg.pre_validation_command,
                cwd=str(repo_root), shell=True, capture_output=True,
                text=True, timeout=cfg.test_timeout,
            )
            if fmt.returncode == 0:
                log("  [harness] formatting applied (or already clean)")
            else:
                # Non-fatal: log and continue; validation will catch real problems.
                log(f"  [harness] formatting step returned exit {fmt.returncode} (continuing)")
        except Exception as e:
            log(f"  [harness] formatting step error: {type(e).__name__}: {e} (continuing)")

    cmd = cfg.resolved_test_command()
    log(f"  [harness] running validation: {cmd}")
    log(f"  [harness] cwd: {repo_root}")

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            shell=True,                # needed for mvnw.cmd on Windows
            capture_output=True,
            text=True,
            timeout=cfg.test_timeout,
        )
    except subprocess.TimeoutExpired:
        return ValidationResult(False, -1, "TIMEOUT", f"test run exceeded {cfg.test_timeout}s")
    except Exception as e:
        return ValidationResult(False, -2, f"ERROR: {type(e).__name__}: {e}", "")

    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    tail = "\n".join(out.splitlines()[-25:])  # last lines hold the BUILD result

    passed = proc.returncode == 0
    # Maven prints BUILD SUCCESS / BUILD FAILURE; use exit code as source of truth,
    # the text scan is only for a friendlier summary line.
    if "BUILD SUCCESS" in out:
        summary = "BUILD SUCCESS"
    elif "BUILD FAILURE" in out:
        summary = "BUILD FAILURE"
    else:
        summary = f"exit {proc.returncode}"

    # ---- COVERAGE GATE (only if tests passed and a threshold is set) ----
    coverage_note = ""
    if passed and cfg.min_coverage > 0:
        log(f"  [harness] coverage: {cfg.coverage_command}")
        try:
            subprocess.run(cfg.coverage_command, cwd=str(repo_root), shell=True,
                           capture_output=True, text=True, timeout=cfg.test_timeout)
        except Exception as e:
            log(f"  [harness] coverage command error: {e} (continuing to parse if report exists)")

        cov = _parse_coverage(repo_root / cfg.coverage_csv, cfg.coverage_metric)
        if cov is None:
            # Can't measure -> treat as a gate failure (don't silently pass).
            passed = False
            summary = "COVERAGE UNREADABLE"
            coverage_note = f"Could not read {cfg.coverage_metric} coverage from {cfg.coverage_csv}"
            log("  ! " + coverage_note)
        elif cov < cfg.min_coverage:
            passed = False
            summary = f"COVERAGE {cov:.1f}% < {cfg.min_coverage:.1f}%"
            coverage_note = (f"{cfg.coverage_metric} coverage {cov:.1f}% is below the "
                             f"required {cfg.min_coverage:.1f}%")
            log("  ! " + coverage_note)
        else:
            coverage_note = f"{cfg.coverage_metric} coverage {cov:.1f}% (>= {cfg.min_coverage:.1f}%)"
            log(f"  [harness] {coverage_note}")

    # Write a validation report into the workspace (auditable artifact).
    # NOTE: petclinic's nohttp checkstyle scans the whole tree including .harness/,
    # and would flag any literal http:// URL we capture from Maven output. Neutralize
    # such URLs in the persisted report so our own audit file can't fail the build.
    report = harness_dir / "validation-report.txt"
    safe_tail = tail.replace("http://", "hxxp://")
    cov_line = f"coverage: {coverage_note}\n" if coverage_note else ""
    try:
        report.write_text(
            f"command: {cmd}\nexit_code: {proc.returncode}\nsummary: {summary}\n{cov_line}\n--- tail ---\n{safe_tail}\n",
            encoding="utf-8",
        )
    except Exception:
        pass

    final_tail = tail if not coverage_note else (tail + "\n\nCOVERAGE: " + coverage_note)
    return ValidationResult(passed, proc.returncode, summary, final_tail)
