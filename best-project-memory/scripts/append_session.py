#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append a structured session entry to .codex-memory/session-log.md."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument("--task", required=True, help="Task summary.")
    parser.add_argument("--actions", default="", help="Actions taken.")
    parser.add_argument("--results", default="", help="Results achieved.")
    parser.add_argument("--next", dest="next_step", default="", help="Next step.")
    parser.add_argument("--blockers", default="None.", help="Current blockers.")
    parser.add_argument(
        "--timestamp",
        default="",
        help="Override timestamp in 'YYYY-MM-DD HH:mm' format.",
    )
    return parser.parse_args()


def build_entry(args: argparse.Namespace) -> str:
    timestamp = args.timestamp or datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"\n## {timestamp}\n"
        f"- Task: {args.task}\n"
        f"- Actions: {args.actions}\n"
        f"- Results: {args.results}\n"
        f"- Next: {args.next_step}\n"
        f"- Blockers: {args.blockers}\n"
    )


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    log_path = repo / ".codex-memory" / "session-log.md"
    if not log_path.exists():
        raise SystemExit(f"Missing session log: {log_path}")

    entry = build_entry(args)
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(entry)

    print(log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
