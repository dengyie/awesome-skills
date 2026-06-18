#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture a repo-state snapshot into .codex-memory/snapshots/."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument(
        "--slug",
        default="branch-state",
        help="Snapshot topic slug used in the filename.",
    )
    parser.add_argument(
        "--validation-state",
        default="Not yet recorded.",
        help="Short verification or validation status summary.",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional note line for extra context.",
    )
    parser.add_argument(
        "--write-project-state",
        action="store_true",
        help="Also update the 'Last Verified' section in project-state.md if present.",
    )
    return parser.parse_args()


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def detect_branch(repo: Path) -> str:
    commands = [
        ("symbolic-ref", "--quiet", "--short", "HEAD"),
        ("rev-parse", "--abbrev-ref", "HEAD"),
    ]
    for command in commands:
        result = subprocess.run(
            ["git", *command],
            cwd=repo,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            value = result.stdout.strip()
            if value:
                return value
    return "unknown"


def bullet_lines(items: list[str], empty_text: str) -> str:
    if not items:
        return f"- {empty_text}\n"
    return "".join(f"- {item}\n" for item in items)


def replace_section(text: str, heading: str, body_lines: list[str]) -> str:
    lines = text.splitlines()
    new_lines: list[str] = []
    i = 0
    replaced = False

    while i < len(lines):
        line = lines[i]
        if line == heading:
            replaced = True
            new_lines.append(line)
            new_lines.extend(body_lines)
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        new_lines.append(line)
        i += 1

    if not replaced:
        if new_lines and new_lines[-1] != "":
            new_lines.append("")
        new_lines.append(heading)
        new_lines.extend(body_lines)

    return "\n".join(new_lines) + "\n"


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    memory_dir = repo / ".codex-memory"
    snapshot_dir = memory_dir / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    slug = args.slug.strip().lower().replace("_", "-").replace(" ", "-")

    branch = detect_branch(repo)
    status_output = run_git(repo, "status", "--short")
    changed_files = []
    if status_output:
        changed_files = [line[3:] if len(line) > 3 else line for line in status_output.splitlines()]

    snapshot_path = snapshot_dir / f"{date_prefix}-{slug}.md"
    content = (
        "# Snapshot\n\n"
        "## Captured At\n"
        f"- {timestamp}\n\n"
        "## Branch\n"
        f"- {branch}\n\n"
        "## Changed Files\n"
        f"{bullet_lines(changed_files, 'No changed files detected.')}\n"
        "## Validation State\n"
        f"- {args.validation_state}\n\n"
        "## Notes\n"
        f"- {args.notes or 'None.'}\n"
    )
    snapshot_path.write_text(content, encoding="utf-8")

    if args.write_project_state:
        state_path = memory_dir / "project-state.md"
        if state_path.exists():
            original = state_path.read_text(encoding="utf-8")
            updated = replace_section(
                original,
                "## Last Verified",
                [f"- {args.validation_state}", f"- Snapshot: `{snapshot_path.name}`"],
            )
            state_path.write_text(updated, encoding="utf-8")

    print(snapshot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
