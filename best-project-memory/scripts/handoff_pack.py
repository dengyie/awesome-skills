#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a compact handoff file from current .codex-memory state."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument("--slug", required=True, help="Short handoff topic slug.")
    parser.add_argument("--objective", required=True, help="Current objective.")
    parser.add_argument(
        "--current-state",
        default="",
        help="Short current-state summary.",
    )
    parser.add_argument(
        "--next-actions",
        nargs="+",
        default=[],
        help="Concrete next actions.",
    )
    parser.add_argument(
        "--read-first",
        nargs="*",
        default=[],
        help="Files to read first.",
    )
    parser.add_argument("--blockers", default="None.", help="Current blockers.")
    parser.add_argument(
        "--validation",
        nargs="*",
        default=[],
        help="Validation steps still to run.",
    )
    return parser.parse_args()


def bullet_lines(items: list[str], empty_text: str) -> str:
    if not items:
        return f"- {empty_text}\n"
    return "".join(f"- {item}\n" for item in items)


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    handoff_dir = repo / ".codex-memory" / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    date_prefix = datetime.now().strftime("%Y-%m-%d")
    handoff_path = handoff_dir / f"{date_prefix}-{args.slug}-handoff.md"

    content = (
        "# Handoff\n\n"
        "## Objective\n"
        f"- {args.objective}\n\n"
        "## Current State\n"
        f"- {args.current_state or 'State summary pending.'}\n\n"
        "## Read First\n"
        f"{bullet_lines(args.read_first, 'None specified.')}\n"
        "## Exact Next Actions\n"
        f"{bullet_lines(args.next_actions, 'Define the immediate next action.')}\n"
        "## Blockers\n"
        f"- {args.blockers}\n\n"
        "## Validation To Run\n"
        f"{bullet_lines(args.validation, 'None specified.')}"
    )

    handoff_path.write_text(content, encoding="utf-8")
    print(handoff_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
