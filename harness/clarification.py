"""
clarification.py — the NEEDS CLARIFICATION gate.

After the context phase, the harness scans the written context file for
`[NEEDS CLARIFICATION]` markers (the contract emitted by the build-context skill
in non-interactive mode). If any remain, the run must NOT proceed to prompt_steps:
the story is ambiguous and a human must resolve it (edit the story) and re-run.

This turns the skill's "I'm unsure" into a hard harness halt — ambiguity can never
be silently guessed into code.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path

MARKER = "[NEEDS CLARIFICATION]"


@dataclass
class ClarificationResult:
    clear: bool
    scanned_file: str
    items: list = field(default_factory=list)  # the clarification lines found


def _newest_context_file(repo_root: Path, search_dir: str) -> Path | None:
    d = repo_root / search_dir
    if not d.is_dir():
        return None
    candidates = sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def scan_clarifications(repo_root: Path,
                        search_dir: str = ".github/story-context-files") -> ClarificationResult:
    """Find the newest context file and extract any [NEEDS CLARIFICATION] lines."""
    f = _newest_context_file(repo_root, search_dir)
    if f is None:
        # No context file at all => treat as not-clear (can't verify), surface clearly.
        return ClarificationResult(clear=False, scanned_file=f"(none in {search_dir})",
                                   items=["No context file was produced to scan."])
    text = f.read_text(encoding="utf-8", errors="replace")
    items = []
    for line in text.splitlines():
        if MARKER in line:
            # keep the human-readable part after the marker
            cleaned = line.strip().lstrip("-").strip()
            items.append(cleaned)
    return ClarificationResult(clear=(len(items) == 0), scanned_file=str(f), items=items)
