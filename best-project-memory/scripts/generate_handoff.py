#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a handoff from current .codex-memory state."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument("--slug", required=True, help="Short handoff topic slug.")
    parser.add_argument(
        "--objective",
        default="",
        help="Override the objective instead of reading project-state.md.",
    )
    parser.add_argument(
        "--current-state",
        default="",
        help="Override current-state summary instead of reading project-state.md/workstream.",
    )
    parser.add_argument(
        "--workstream",
        default="",
        help="Optional workstream slug to draw files, validation, and next actions from.",
    )
    parser.add_argument(
        "--read-first",
        nargs="*",
        default=[],
        help="Additional files to prepend to the read-first list.",
    )
    parser.add_argument(
        "--next-actions",
        nargs="*",
        default=[],
        help="Explicit next actions. Falls back to workstream/todo data when omitted.",
    )
    parser.add_argument("--blockers", default="", help="Override blocker summary.")
    parser.add_argument(
        "--validation",
        nargs="*",
        default=[],
        help="Explicit validation steps. Falls back to workstream validation when omitted.",
    )
    return parser.parse_args()


def normalize_slug(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def extract_section(lines: list[str], heading: str) -> list[str]:
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


def clean_bullets(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        value = line
        for prefix in ("- [ ] ", "- [x] ", "- "):
            if value.startswith(prefix):
                value = value[len(prefix):]
                break
        cleaned.append(value.strip("` "))
    return [item for item in cleaned if item]


def bullet_lines(items: list[str], empty_text: str) -> str:
    if not items:
        return f"- {empty_text}\n"
    return "".join(f"- {item}\n" for item in items)


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    memory_dir = repo / ".codex-memory"
    handoff_dir = memory_dir / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    project_state_path = memory_dir / "project-state.md"
    todo_path = memory_dir / "todo.md"

    project_state_lines = read_lines(project_state_path) if project_state_path.exists() else []
    todo_lines = read_lines(todo_path) if todo_path.exists() else []

    workstream_path = None
    workstream_lines: list[str] = []
    if args.workstream:
        workstream_slug = normalize_slug(args.workstream)
        workstream_path = memory_dir / "workstreams" / f"{workstream_slug}.md"
        if workstream_path.exists():
            workstream_lines = read_lines(workstream_path)

    objective = args.objective or " ".join(
        clean_bullets(extract_section(project_state_lines, "## Objective"))
    )
    current_state = args.current_state or " ".join(
        clean_bullets(extract_section(workstream_lines, "## Current State"))
        or clean_bullets(extract_section(project_state_lines, "## Current Focus"))
    )

    blockers = (
        [args.blockers]
        if args.blockers
        else clean_bullets(extract_section(workstream_lines, "## Blockers"))
        or clean_bullets(extract_section(project_state_lines, "## Active Blockers"))
    )

    read_first = list(args.read_first)
    if workstream_path is not None:
        read_first.append(str(workstream_path.relative_to(repo)).replace("\\", "/"))
    read_first.extend(clean_bullets(extract_section(project_state_lines, "## Key Artifacts")))

    next_actions = list(args.next_actions)
    if not next_actions:
        next_actions = clean_bullets(extract_section(workstream_lines, "## Next Actions"))
    if not next_actions:
        next_actions = clean_bullets(extract_section(todo_lines, "## In Progress"))
    if not next_actions:
        next_actions = clean_bullets(extract_section(todo_lines, "## Next"))

    validation = list(args.validation)
    if not validation:
        validation = clean_bullets(extract_section(workstream_lines, "## Validation"))

    date_prefix = datetime.now().strftime("%Y-%m-%d")
    handoff_path = handoff_dir / f"{date_prefix}-{normalize_slug(args.slug)}-handoff.md"
    content = (
        "# Handoff\n\n"
        "## Objective\n"
        f"{bullet_lines([objective] if objective else [], 'Objective not yet defined.')}\n"
        "## Current State\n"
        f"{bullet_lines([current_state] if current_state else [], 'State summary pending.')}\n"
        "## Read First\n"
        f"{bullet_lines(read_first, 'None specified.')}\n"
        "## Exact Next Actions\n"
        f"{bullet_lines(next_actions, 'Define the immediate next action.')}\n"
        "## Blockers\n"
        f"{bullet_lines(blockers, 'None.')}\n"
        "## Validation To Run\n"
        f"{bullet_lines(validation, 'None specified.')}"
    )
    handoff_path.write_text(content, encoding="utf-8")
    print(handoff_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
