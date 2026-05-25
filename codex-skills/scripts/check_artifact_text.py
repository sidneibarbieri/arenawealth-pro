#!/usr/bin/env python3
"""Scan an artifact for avoidable hype, leaked notes, and irrelevant terms."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# Patterns applied to all scanned files
DEFAULT_PATTERNS = {
    "hype": r"\b(world[- ]class|perfect|ultimate|best[- ]in[- ]class|revolutionary)\b",
    "ai_markers": r"(🚀|✨|🤖|as an ai|chatgpt|claude)",
    "security_paste": r"\b(MITRE|STICKS|ATT&CK)\b",
    "secret_assignment": r"\b(api[_-]?key|token|secret)\b\s*[:=]\s*[\"']?[A-Za-z0-9._-]{16,}",
}

# Venue-leak check only applies to executable source, not submission packets
# Scan: src/, frontend/src/, tests/
# Skip: paper/, notes/, ACM_ICAIF/, FinTech_WC/, docs/
VENUE_LEAK_PATTERN = re.compile(r"\b(ICAIF|Top 4|best paper)\b", re.IGNORECASE)
VENUE_LEAK_DIRS = {"src", "frontend"}


def iter_files(root: Path) -> list[Path]:
    ignored_parts = {
        ".git",
        ".venv",
        "codex-skills",
        "node_modules",
        "dist",
        "archive",
        "data",
        "project-framework",
        "exports",  # frozen snapshot artifacts — scan separately if needed
    }
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if ignored_parts.intersection(path.parts):
            continue
        if path.suffix.lower() not in {".md", ".py", ".ts", ".tsx", ".js", ".css", ".tex"}:
            continue
        files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    findings: list[str] = []
    patterns = {
        name: re.compile(pattern, re.IGNORECASE) for name, pattern in DEFAULT_PATTERNS.items()
    }

    for path in iter_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        in_venue_scope = bool(VENUE_LEAK_DIRS.intersection(path.parts))
        for line_number, line in enumerate(text.splitlines(), start=1):
            for name, pattern in patterns.items():
                if pattern.search(line):
                    findings.append(f"{path}:{line_number}: {name}: {line.strip()[:160]}")
            if in_venue_scope and VENUE_LEAK_PATTERN.search(line):
                findings.append(f"{path}:{line_number}: venue_leak: {line.strip()[:160]}")

    if findings:
        print("\n".join(findings))
        return 1
    print("OK: no text hygiene findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
