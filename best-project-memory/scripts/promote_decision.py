#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append a promoted decision entry to .codex-memory/decisions.md."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument("--title", required=True, help="Decision title.")
    parser.add_argument("--decision", required=True, help="Decision summary.")
    parser.add_argument("--rationale", required=True, help="Why the decision was made.")
    parser.add_argument(
        "--alternatives",
        default="Not recorded.",
        help="Alternatives considered.",
    )
    parser.add_argument("--impact", required=True, help="Expected impact.")
    parser.add_argument(
        "--rollback-trigger",
        default="Revisit if evidence changes.",
        help="Rollback or reconsideration trigger.",
    )
    parser.add_argument(
        "--related-files",
        nargs="*",
        default=[],
        help="Related file paths.",
    )
    parser.add_argument(
        "--source-workstream",
        default="",
        help="Optional source workstream slug for traceability.",
    )
    return parser.parse_args()


def normalize_slug(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def format_related_files(files: list[str], source_workstream: str) -> str:
    values = list(files)
    if source_workstream:
        values.append(f".codex-memory/workstreams/{normalize_slug(source_workstream)}.md")
    if not values:
        return "Not recorded."
    return ", ".join(f"`{value}`" for value in values)


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    decisions_path = repo / ".codex-memory" / "decisions.md"
    if not decisions_path.exists():
        raise SystemExit(f"Missing decisions log: {decisions_path}")

    date_prefix = datetime.now().strftime("%Y-%m-%d")
    entry = (
        f"\n## {date_prefix} - {args.title}\n"
        f"- Decision: {args.decision}\n"
        f"- Rationale: {args.rationale}\n"
        f"- Alternatives considered: {args.alternatives}\n"
        f"- Impact: {args.impact}\n"
        f"- Rollback trigger: {args.rollback_trigger}\n"
        f"- Related files: {format_related_files(args.related_files, args.source_workstream)}\n"
    )

    with decisions_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(entry)

    print(decisions_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
