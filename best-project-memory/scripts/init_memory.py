#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


CORE_FILES = {
    "project-state.md": """# Project State

## Objective
- 

## Current Phase
- 

## Current Branch
- 

## Last Verified
- 

## Active Risks
- None.

## Active Blockers
- None.

## Current Focus
- 

## Next Milestone
- 

## Key Artifacts
- 
""",
    "session-log.md": """# Session Log
""",
    "decisions.md": """# Decisions
""",
    "todo.md": """# TODO
## In Progress
- [ ] 
## Next
- [ ] 
## Done
""",
}

OPTIONAL_DIRS = ("phases", "handoffs", "workstreams", "snapshots")

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

SNAPSHOT_TEMPLATE = """# Snapshot

## Captured At
- 

## Branch
- 

## Changed Files
- 

## Validation State
- 

## Notes
- 
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize .codex-memory in a repository."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument(
        "--with-optional-dirs",
        action="store_true",
        help="Also create phases/, handoffs/, workstreams/, and snapshots/ directories.",
    )
    parser.add_argument(
        "--with-governance-dirs",
        action="store_true",
        help="Alias for --with-optional-dirs.",
    )
    parser.add_argument(
        "--default-workstream",
        default="",
        help="Create a starter workstream file at workstreams/<slug>.md.",
    )
    parser.add_argument(
        "--default-snapshot",
        action="store_true",
        help="Create a starter snapshot template in snapshots/.",
    )
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Repair missing memory files and governance directories if they do not exist.",
    )
    return parser.parse_args()


def ensure_file(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def ensure_optional_dirs(memory_dir: Path) -> None:
    for directory in OPTIONAL_DIRS:
        (memory_dir / directory).mkdir(exist_ok=True)


def normalize_slug(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    memory_dir = repo / ".codex-memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    if args.with_optional_dirs or args.with_governance_dirs or args.repair:
        ensure_optional_dirs(memory_dir)

    for name, content in CORE_FILES.items():
        ensure_file(memory_dir / name, content)

    if args.default_workstream:
        ensure_optional_dirs(memory_dir)
        slug = normalize_slug(args.default_workstream)
        ensure_file(memory_dir / "workstreams" / f"{slug}.md", WORKSTREAM_TEMPLATE)

    if args.default_snapshot:
        ensure_optional_dirs(memory_dir)
        ensure_file(memory_dir / "snapshots" / "initial-snapshot.md", SNAPSHOT_TEMPLATE)

    print(memory_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
