#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_FILES = {
    "project-state.md": [
        "## Objective",
        "## Current Phase",
        "## Current Branch",
        "## Last Verified",
        "## Active Risks",
        "## Active Blockers",
        "## Current Focus",
        "## Next Milestone",
        "## Key Artifacts",
    ],
    "todo.md": ["## In Progress", "## Next", "## Done"],
    "session-log.md": [],
    "decisions.md": [],
}

WORKSTREAM_SECTIONS = [
    "## Objective",
    "## Current State",
    "## Blockers",
    "## Files",
    "## Next Actions",
    "## Validation",
]

HANDOFF_SECTIONS = [
    "## Objective",
    "## Current State",
    "## Read First",
    "## Exact Next Actions",
    "## Blockers",
    "## Validation To Run",
]

STRUCTURED_SESSION_ENTRY_RE = re.compile(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}$", re.MULTILINE)
SNAPSHOT_REF_RE = re.compile(r"Snapshot:\s*`([^`]+)`")
SESSION_COMPACTION_WARNING_THRESHOLD = 8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint .codex-memory for missing sections and common quality issues."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def list_markdown_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(path.glob("*.md"))


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


def clean_bullets(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        value = line
        for prefix in ("- [ ] ", "- [x] ", "- "):
            if value.startswith(prefix):
                value = value[len(prefix):]
                break
        value = value.strip("` ")
        if value:
            items.append(value)
    return items


def parse_snapshot_reference(project_state: str) -> str:
    match = SNAPSHOT_REF_RE.search(project_state)
    if not match:
        return ""
    return match.group(1).strip()


def snapshot_has_changed_files(text: str) -> bool:
    items = clean_bullets(extract_section(text, "## Changed Files"))
    if not items:
        return False
    return items != ["No changed files detected."]


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    memory_dir = repo / ".codex-memory"
    errors: list[str] = []
    warnings: list[str] = []

    if not memory_dir.exists():
        print("ERROR: Missing .codex-memory directory")
        return 1

    for filename, sections in REQUIRED_FILES.items():
        path = memory_dir / filename
        if not path.exists():
            errors.append(f"Missing required file: {filename}")
            continue
        text = read_text(path)
        for heading in sections:
            if heading not in text:
                errors.append(f"{filename}: missing section {heading}")

    decisions_path = memory_dir / "decisions.md"
    if decisions_path.exists():
        decisions_text = read_text(decisions_path)
        entries = [part for part in decisions_text.split("\n## ") if part.strip()]
        for entry in entries:
            if "Decision:" in entry and "Rationale:" not in entry:
                errors.append("decisions.md: a decision entry is missing Rationale")

    for workstream_path in list_markdown_files(memory_dir / "workstreams"):
        text = read_text(workstream_path)
        for heading in WORKSTREAM_SECTIONS:
            if heading not in text:
                errors.append(f"{workstream_path.name}: missing section {heading}")
        next_actions = clean_bullets(extract_section(text, "## Next Actions"))
        if not next_actions:
            warnings.append(f"{workstream_path.name}: no next actions recorded")

    for handoff_path in list_markdown_files(memory_dir / "handoffs"):
        text = read_text(handoff_path)
        for heading in HANDOFF_SECTIONS:
            if heading not in text:
                errors.append(f"{handoff_path.name}: missing section {heading}")
        next_actions = clean_bullets(extract_section(text, "## Exact Next Actions"))
        if not next_actions:
            errors.append(f"{handoff_path.name}: missing exact next actions")

    todo_path = memory_dir / "todo.md"
    if todo_path.exists():
        todo_text = read_text(todo_path)
        in_progress = clean_bullets(extract_section(todo_text, "## In Progress"))
        if len(in_progress) > 5:
            warnings.append("todo.md: more than 5 items in In Progress")

    project_state_path = memory_dir / "project-state.md"
    if project_state_path.exists():
        project_state = read_text(project_state_path)
        snapshot_reference = parse_snapshot_reference(project_state)
        blockers = clean_bullets(extract_section(project_state, "## Active Blockers"))
        if blockers and blockers != ["None."]:
            for workstream_path in list_markdown_files(memory_dir / "workstreams"):
                text = read_text(workstream_path)
                workstream_blockers = clean_bullets(extract_section(text, "## Blockers"))
                if workstream_blockers == ["None."]:
                    warnings.append(
                        f"{workstream_path.name}: project-state has active blockers but workstream says None."
                    )
        if snapshot_reference:
            snapshot_path = memory_dir / "snapshots" / snapshot_reference
            if not snapshot_path.exists():
                errors.append(
                    f"project-state.md: referenced snapshot does not exist: {snapshot_reference}"
                )

    session_log_path = memory_dir / "session-log.md"
    if session_log_path.exists():
        session_log_text = read_text(session_log_path)
        entry_count = len(STRUCTURED_SESSION_ENTRY_RE.findall(session_log_text))
        has_compacted_history = "## Compacted History" in session_log_text
        if entry_count > SESSION_COMPACTION_WARNING_THRESHOLD and not has_compacted_history:
            warnings.append(
                "session-log.md: structured history is getting long and should be compacted"
            )

    snapshots_dir = memory_dir / "snapshots"
    snapshots = list_markdown_files(snapshots_dir)
    if snapshots:
        latest_snapshot = snapshots[-1]
        latest_snapshot_text = read_text(latest_snapshot)
        if snapshot_has_changed_files(latest_snapshot_text) and project_state_path.exists():
            project_state = read_text(project_state_path)
            snapshot_reference = parse_snapshot_reference(project_state)
            if not snapshot_reference:
                warnings.append(
                    f"project-state.md: latest snapshot `{latest_snapshot.name}` shows changed files but project-state does not reference a snapshot"
                )
            elif snapshot_reference != latest_snapshot.name:
                warnings.append(
                    f"project-state.md: latest snapshot `{latest_snapshot.name}` shows changed files but project-state still references `{snapshot_reference}`"
                )

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1
    print("Memory lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
