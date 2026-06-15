#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import sys


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
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format.",
    )
    args = parser.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    context = lib.collect_review_context(repo)

    if args.format == "json":
        sys.stdout.write(lib.to_pretty_json(context))
    else:
        sys.stdout.write(lib.build_review_brief_markdown(context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
