#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


STALE_TOKENS = (
    "keep improving",
    "follow up later",
    "misc",
    "cleanup",
    "stuff",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check .codex-memory/todo.md for stale or weakly actionable TODO items."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    capture = False
    section: list[str] = []
    for line in lines:
        if line == heading:
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture:
            stripped = line.strip()
            if stripped:
                section.append(stripped)
    return section


def clean_items(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        value = line
        for prefix in ("- [ ] ", "- [x] ", "- "):
            if value.startswith(prefix):
                value = value[len(prefix):]
                break
        value = value.strip()
        if value:
            items.append(value)
    return items


def is_stale(item: str) -> bool:
    lowered = item.lower()
    if len(lowered.split()) <= 1:
        return True
    return any(token in lowered for token in STALE_TOKENS)


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    todo_path = repo / ".codex-memory" / "todo.md"
    if not todo_path.exists():
        print("ERROR: Missing .codex-memory/todo.md")
        return 1

    text = read_text(todo_path)
    issues: list[str] = []

    for heading in ("## In Progress", "## Next"):
        items = clean_items(extract_section(text, heading))
        for item in items:
            if is_stale(item):
                issues.append(f"{heading}: '{item}' looks stale or too vague")

    if issues:
        for issue in issues:
            print(f"WARNING: {issue}")
        return 1

    print("No stale TODO items detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
