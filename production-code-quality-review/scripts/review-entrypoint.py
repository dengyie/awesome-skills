#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import sys


sys.dont_write_bytecode = True
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import review_skill_lib as lib


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an actionable review brief from deterministic repo context."
    )
    parser.add_argument("--repo", default=".", help="Path to the git repository.")
    parser.add_argument(
        "--base",
        default=None,
        help="Optional explicit base ref override, such as HEAD or origin/main.",
    )
    parser.add_argument(
        "--scope",
        choices=["branch", "working_tree"],
        default=None,
        help="Optional review scope mode override.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "compact"],
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--append-memory-session",
        action="store_true",
        help="Append a structured review session entry when .codex-memory is present.",
    )
    parser.add_argument(
        "--review-status",
        choices=["passed", "conditional", "failed"],
        default="passed",
        help="Review outcome recorded when appending continuity to project memory.",
    )
    parser.add_argument(
        "--review-score",
        type=int,
        default=85,
        help="Quality score recorded in appended review continuity notes.",
    )
    parser.add_argument(
        "--todo-follow-up",
        nargs="*",
        default=[],
        help="Optional review follow-up items to merge into .codex-memory/todo.md.",
    )
    args = parser.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    context = lib.collect_review_context(
        repo,
        base_ref_override=args.base,
        scope_mode_override=args.scope,
    )
    if args.append_memory_session or args.todo_follow_up:
        lib.record_review_memory(
            repo,
            context,
            review_status=args.review_status,
            review_score=args.review_score,
            todo_follow_ups=args.todo_follow_up,
            append_session=args.append_memory_session,
        )

    if args.format == "json":
        sys.stdout.write(lib.to_pretty_json(context))
    elif args.format == "compact":
        sys.stdout.write(lib.build_review_brief_compact(context))
    else:
        sys.stdout.write(lib.build_review_brief_markdown(context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
