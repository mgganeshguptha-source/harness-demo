"""
review.py — the CODE REVIEW gate.

After the code_review phase, an INDEPENDENT reviewer LLM (a model different from
the one that wrote the code) inspects the change and writes a structured verdict
to .harness/review.md. The harness parses that verdict deterministically:

  - VERDICT: PASS                 -> advance to unit_testing
  - VERDICT: CHANGES_REQUESTED    -> loop back to coding with the issues as
                                     feedback (bounded by max_review_retries)

The verdict is machine-readable on purpose (same philosophy as the clarification
gate): the harness owns the decision from a canonical marker, not from prose. The
issues list becomes the coding phase's feedback verbatim.

Expected review.md shape (reviewer is instructed to emit exactly this):

    VERDICT: CHANGES_REQUESTED
    [ISSUE]: Owner.hasPet does not handle null name -> NPE risk
    [ISSUE]: equalsIgnoreCase called on the argument, not the field
    ...free-form review notes may follow...

or:

    VERDICT: PASS
    ...optional commentary...
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path

_VERDICT = re.compile(r"^\s*VERDICT\s*:\s*(PASS|CHANGES_REQUESTED|FAIL|APPROVE|APPROVED)\b",
                      re.IGNORECASE | re.MULTILINE)
_ISSUE = re.compile(r"^\s*(?:[-*>\s]*)?\[ISSUE\]\s*:\s*(\S.*)$", re.IGNORECASE | re.MULTILINE)

_PASS_TOKENS = {"pass", "approve", "approved"}


@dataclass
class ReviewResult:
    passed: bool
    verdict: str | None          # normalized: "PASS" | "CHANGES_REQUESTED" | None
    issues: list = field(default_factory=list)
    scanned_file: str = ""
    parse_ok: bool = True        # False when no VERDICT marker was found


def parse_review(review_file: Path) -> ReviewResult:
    """Parse the reviewer's verdict file. Missing file or missing VERDICT marker
    is treated as NOT passed (fail-closed): a reviewer that didn't emit a verdict
    should not silently advance the change."""
    if not review_file.exists():
        return ReviewResult(passed=False, verdict=None, issues=[],
                            scanned_file=str(review_file),
                            parse_ok=False)
    text = review_file.read_text(encoding="utf-8", errors="replace")

    m = _VERDICT.search(text)
    if not m:
        # No canonical verdict -> fail-closed, flag as unparseable.
        return ReviewResult(passed=False, verdict=None, issues=[],
                            scanned_file=str(review_file), parse_ok=False)

    tok = m.group(1).lower()
    passed = tok in _PASS_TOKENS
    verdict = "PASS" if passed else "CHANGES_REQUESTED"

    issues = [i.strip() for i in _ISSUE.findall(text) if i.strip()]
    # If the reviewer said CHANGES_REQUESTED but listed no [ISSUE] lines, keep a
    # generic placeholder so the coding phase still gets actionable feedback.
    if not passed and not issues:
        issues = ["Reviewer requested changes but did not enumerate [ISSUE] items; "
                  "see review.md for prose notes."]
    return ReviewResult(passed=passed, verdict=verdict, issues=issues,
                        scanned_file=str(review_file), parse_ok=True)
