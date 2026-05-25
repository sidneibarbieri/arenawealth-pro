#!/usr/bin/env python3
"""Validate a local Codex skill package."""

from __future__ import annotations

import re
import sys
from pathlib import Path


FRONTMATTER_PATTERN = re.compile(
    r"^---\nname: (?P<name>[a-z0-9-]+)\ndescription: (?P<description>.+?)\n",
    re.DOTALL,
)


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    skill_file = path / "SKILL.md"
    if not skill_file.exists():
        return [f"{path.name}: missing SKILL.md"]

    text = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        errors.append(f"{path.name}: invalid frontmatter")
        return errors

    if match.group("name") != path.name:
        errors.append(f"{path.name}: frontmatter name does not match directory")
    if len(match.group("description")) < 80:
        errors.append(f"{path.name}: description is too short for reliable triggering")
    if len(text.splitlines()) > 500:
        errors.append(f"{path.name}: SKILL.md is longer than 500 lines")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    skill_dirs = sorted(path for path in root.iterdir() if (path / "SKILL.md").exists())
    errors: list[str] = []
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))

    if not skill_dirs:
        errors.append("no skill directories found")

    if errors:
        for error in errors:
            print(error)
        return 1

    print(f"OK: {len(skill_dirs)} skills validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

