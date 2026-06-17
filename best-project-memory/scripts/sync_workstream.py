#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


WORKSTREAM_TEMPLATE = """# Workstream

## Objective
- 

## Current State
- 

## Blockers
- None.

## Files
- 

## Next Actions
- [ ] 

## Validation
- Not yet run.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update a workstream file in .codex-memory/workstreams/."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument("--slug", required=True, help="Workstream slug.")
    parser.add_argument("--objective", default="", help="Workstream objective.")
    parser.add_argument(
        "--current-state",
        default="",
        help="Short current state summary.",
    )
    parser.add_argument(
        "--blockers",
        nargs="*",
        default=[],
        help="Blocker bullets.",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=[],
        help="Relevant file paths.",
    )
    parser.add_argument(
        "--next-actions",
        nargs="*",
        default=[],
        help="Next-action checklist items.",
    )
    parser.add_argument(
        "--validation",
        default="",
        help="Validation status summary.",
    )
    return parser.parse_args()


def normalize_slug(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def bullet_lines(items: list[str], empty_text: str) -> str:
    if not items:
        return f"- {empty_text}\n"
    return "".join(f"- {item}\n" for item in items)


def checklist_lines(items: list[str], empty_text: str) -> str:
    if not items:
        return f"- [ ] {empty_text}\n"
    return "".join(f"- [ ] {item}\n" for item in items)


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    memory_dir = repo / ".codex-memory"
    workstream_dir = memory_dir / "workstreams"
    workstream_dir.mkdir(parents=True, exist_ok=True)

    slug = normalize_slug(args.slug)
    workstream_path = workstream_dir / f"{slug}.md"
    if not workstream_path.exists():
        workstream_path.write_text(WORKSTREAM_TEMPLATE, encoding="utf-8")

    content = (
        "# Workstream\n\n"
        "## Objective\n"
        f"- {args.objective or 'Objective not yet defined.'}\n\n"
        "## Current State\n"
        f"- {args.current_state or 'State summary pending.'}\n\n"
        "## Blockers\n"
        f"{bullet_lines(args.blockers, 'None.')}\n"
        "## Files\n"
        f"{bullet_lines(args.files, 'None recorded.')}\n"
        "## Next Actions\n"
        f"{checklist_lines(args.next_actions, 'Define the next action.')}\n"
        "## Validation\n"
        f"- {args.validation or 'Not yet run.'}\n"
    )
    workstream_path.write_text(content, encoding="utf-8")

    print(workstream_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
