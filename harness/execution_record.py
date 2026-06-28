"""
execution_record.py — appends a factual EXECUTION RECORD to the prompt-steps audit
file after the coding phase, and stamps human approval at the gate.

Design contract:
  - The approved plan (Impacted Files block + steps) is NEVER mutated.
  - The harness APPENDS an EXECUTION RECORD section capturing what coding actually
    did: files touched, and any SCOPE ADDITION (touched but not in the approved
    Impacted Files block). The model cannot forge this — it's harness-written from
    the permission-handler's attempted_writes.
  - End of coding => append the factual record (regardless of approve/reject).
  - On approval => stamp "reviewed & approved" onto the latest record.

This gives a true before/after audit: planned vs executed vs reviewed.
"""
from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path

RECORD_HEADER = "## --- EXECUTION RECORD (appended by harness) ---"


def _approved_paths_from_plan(plan_text: str) -> set[str]:
    """Extract file paths from the Impacted Files markdown table.
    Rows look like: | F1 | src/main/java/.../Owner.java | role |
    """
    paths = set()
    in_table = False
    for line in plan_text.splitlines():
        if "Impacted Files" in line:
            in_table = True
            continue
        if in_table:
            # table rows start with |
            if line.strip().startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                # need at least ID | path | role ; skip header/separator rows
                if len(cells) >= 2 and cells[1] and not set(cells[1]) <= {"-", " "} \
                        and cells[0].upper() not in ("ID",):
                    paths.add(_norm(cells[1]))
            elif line.strip() and not line.strip().startswith(">"):
                # left the table block
                if line.startswith("#"):
                    in_table = False
    return {p for p in paths if p and "/" in p}


def _norm(p: str) -> str:
    p = p.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p.lstrip("/")


def _rel_to_repo(path: str, repo_root: Path) -> str:
    p = path.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    root = str(repo_root).replace("\\", "/").rstrip("/")
    if p.lower().startswith(root.lower() + "/"):
        return p[len(root) + 1:]
    return p.lstrip("/")


def append_execution_record(plan_file: Path, repo_root: Path,
                            attempted_writes: list, phase_id: str) -> dict:
    """Append a factual execution record. Returns a summary dict (incl. scope_additions)."""
    plan_text = plan_file.read_text(encoding="utf-8") if plan_file.exists() else ""
    approved = _approved_paths_from_plan(plan_text)

    # actual files touched during coding, repo-relative, source files only
    actual = sorted({
        _rel_to_repo(w, repo_root) for w in attempted_writes
        if "/" in _norm(w) and not _norm(w).startswith(".harness")
    })
    actual_set = set(actual)

    # scope additions = touched but not in the approved plan
    additions = sorted(a for a in actual_set if a not in approved)

    ts = datetime.now().isoformat(timespec="seconds")
    lines = [
        "",
        RECORD_HEADER,
        f"- timestamp: {ts}",
        f"- phase: {phase_id}",
        f"- approved impacted files: {sorted(approved) if approved else '(none parsed)'}",
        f"- actually touched: {actual if actual else '(none)'}",
    ]
    if additions:
        lines.append(f"- ⚠ SCOPE ADDITION (touched, not in approved plan): {additions}")
        lines.append("  -> review this scope change before approving the coding phase.")
    else:
        lines.append("- scope: matches approved plan (no additions)")
    lines.append("- review status: PENDING (awaiting coding-gate approval)")
    lines.append("")

    with plan_file.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {"approved": sorted(approved), "actual": actual,
            "scope_additions": additions}


def stamp_approval(plan_file: Path, approved: bool, feedback: str = "") -> None:
    """Update the latest EXECUTION RECORD's review status with the human decision."""
    if not plan_file.exists():
        return
    text = plan_file.read_text(encoding="utf-8")
    ts = datetime.now().isoformat(timespec="seconds")
    verdict = "APPROVED" if approved else "REJECTED"
    stamp = f"- review status: {verdict} by human at {ts}"
    if feedback:
        stamp += f" — feedback: {feedback}"
    # replace the LAST 'review status: PENDING' line
    pending = "- review status: PENDING (awaiting coding-gate approval)"
    idx = text.rfind(pending)
    if idx != -1:
        text = text[:idx] + stamp + text[idx + len(pending):]
        plan_file.write_text(text, encoding="utf-8")
