#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ENTRY_HEADER_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2})$")
FIELD_PREFIXES = (
    "- Task: ",
    "- Actions: ",
    "- Results: ",
    "- Next: ",
    "- Blockers: ",
)


@dataclass
class SessionEntry:
    timestamp: str
    task: str
    actions: str
    results: str
    next_step: str
    blockers: str
    raw_lines: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compact older structured session-log entries into a shorter summary block."
    )
    parser.add_argument("--repo", default=".", help="Repository root path.")
    parser.add_argument(
        "--keep-last",
        type=int,
        default=3,
        help="How many recent entries to keep verbatim in session-log.md.",
    )
    parser.add_argument(
        "--max-entries",
        type=int,
        default=6,
        help="Only compact when the log contains more than this many structured entries.",
    )
    parser.add_argument(
        "--phase-slug",
        default="",
        help="Optional phase summary slug to also write under .codex-memory/phases/.",
    )
    parser.add_argument(
        "--title",
        default="Compacted Session History",
        help="Override the summary block title.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without rewriting files.",
    )
    return parser.parse_args()


def normalize_slug(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def parse_entries(text: str) -> tuple[str, list[SessionEntry]]:
    lines = text.splitlines()
    if not lines:
        return "", []

    header_lines: list[str] = []
    entries: list[SessionEntry] = []
    i = 0

    while i < len(lines) and not ENTRY_HEADER_RE.match(lines[i]):
        header_lines.append(lines[i])
        i += 1

    while i < len(lines):
        match = ENTRY_HEADER_RE.match(lines[i])
        if not match:
            break

        timestamp = match.group(1)
        block_lines = [lines[i]]
        i += 1
        while i < len(lines) and not ENTRY_HEADER_RE.match(lines[i]):
            block_lines.append(lines[i])
            i += 1

        parsed = parse_entry_block(timestamp, block_lines)
        if parsed is None:
            break
        entries.append(parsed)

    return "\n".join(header_lines).rstrip(), entries


def parse_entry_block(timestamp: str, block_lines: list[str]) -> SessionEntry | None:
    fields: dict[str, str] = {}
    for line in block_lines[1:]:
        for prefix in FIELD_PREFIXES:
            if line.startswith(prefix):
                fields[prefix] = line[len(prefix) :].strip()
                break

    if any(prefix not in fields for prefix in FIELD_PREFIXES):
        return None

    return SessionEntry(
        timestamp=timestamp,
        task=fields["- Task: "],
        actions=fields["- Actions: "],
        results=fields["- Results: "],
        next_step=fields["- Next: "],
        blockers=fields["- Blockers: "],
        raw_lines=block_lines,
    )


def summarize_entries(title: str, entries: list[SessionEntry]) -> str:
    first = entries[0].timestamp
    last = entries[-1].timestamp
    tasks = dedupe_preserve_order(entry.task for entry in entries if entry.task)
    results = dedupe_preserve_order(entry.results for entry in entries if entry.results)
    next_steps = dedupe_preserve_order(
        entry.next_step
        for entry in entries
        if entry.next_step and entry.next_step.lower() not in {"none.", "none"}
    )
    blockers = dedupe_preserve_order(
        entry.blockers
        for entry in entries
        if entry.blockers and entry.blockers.lower() not in {"none.", "none"}
    )

    lines = [
        "## Compacted History",
        f"- Title: {title}",
        f"- Covered entries: {len(entries)}",
        f"- Date range: {first} -> {last}",
        "",
        "### Task Themes",
    ]
    if tasks:
        lines.extend(f"- {task}" for task in tasks[:6])
    else:
        lines.append("- None recorded.")
    lines.extend(["", "### Results Preserved"])
    if results:
        lines.extend(f"- {result}" for result in results[:6])
    else:
        lines.append("- None recorded.")
    lines.extend(["", "### Historical Next-Step Themes"])
    if next_steps:
        lines.extend(f"- {item}" for item in next_steps[:6])
    else:
        lines.append("- None recorded.")
    lines.extend(["", "### Unresolved Historical Blockers"])
    if blockers:
        lines.extend(f"- {item}" for item in blockers[:6])
    else:
        lines.append("- None.")
    return "\n".join(lines).rstrip() + "\n"


def dedupe_preserve_order(items) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def format_entries(entries: list[SessionEntry]) -> str:
    blocks: list[str] = []
    for entry in entries:
        blocks.append("\n".join(entry.raw_lines).rstrip())
    return "\n\n".join(blocks).rstrip() + "\n"


def build_phase_summary(title: str, entries: list[SessionEntry]) -> str:
    first = entries[0].timestamp
    last = entries[-1].timestamp
    tasks = dedupe_preserve_order(entry.task for entry in entries if entry.task)
    results = dedupe_preserve_order(entry.results for entry in entries if entry.results)
    blockers = dedupe_preserve_order(
        entry.blockers
        for entry in entries
        if entry.blockers and entry.blockers.lower() not in {"none.", "none"}
    )
    next_steps = dedupe_preserve_order(
        entry.next_step
        for entry in entries
        if entry.next_step and entry.next_step.lower() not in {"none.", "none"}
    )

    lines = [
        "# Phase Summary",
        "",
        "## Goal",
        f"- {title}",
        "",
        "## Covered Range",
        f"- {first} -> {last}",
        "",
        "## Outcomes",
    ]
    if results:
        lines.extend(f"- {item}" for item in results[:8])
    else:
        lines.append("- No durable outcomes recorded.")
    lines.extend(["", "## Key Work Themes"])
    if tasks:
        lines.extend(f"- {item}" for item in tasks[:8])
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## Open Risks Or Blockers"])
    if blockers:
        lines.extend(f"- {item}" for item in blockers[:8])
    else:
        lines.append("- None carried forward from the compacted range.")
    lines.extend(["", "## Next Entry Condition"])
    if next_steps:
        lines.extend(f"- {item}" for item in next_steps[:5])
    else:
        lines.append("- Continue from the most recent un-compacted session entries.")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    if args.keep_last < 1:
        raise SystemExit("--keep-last must be at least 1")
    if args.max_entries < 1:
        raise SystemExit("--max-entries must be at least 1")

    repo = Path(args.repo).resolve()
    memory_dir = repo / ".codex-memory"
    log_path = memory_dir / "session-log.md"
    if not log_path.exists():
        raise SystemExit(f"Missing session log: {log_path}")

    text = log_path.read_text(encoding="utf-8")
    header, entries = parse_entries(text)
    if len(entries) <= args.max_entries:
        print(f"No compaction needed: {len(entries)} structured entries <= threshold {args.max_entries}.")
        return 0

    if len(entries) <= args.keep_last:
        print(f"No compaction applied: {len(entries)} structured entries <= keep-last {args.keep_last}.")
        return 0

    compacted = entries[:-args.keep_last]
    retained = entries[-args.keep_last:]
    summary_block = summarize_entries(args.title, compacted)

    parts: list[str] = []
    if header:
        parts.append(header.rstrip())
    parts.append(summary_block.rstrip())
    parts.append(format_entries(retained).rstrip())
    new_text = "\n\n".join(part for part in parts if part).rstrip() + "\n"

    phase_output = ""
    phase_path: Path | None = None
    if args.phase_slug:
        phase_dir = memory_dir / "phases"
        phase_dir.mkdir(parents=True, exist_ok=True)
        date_prefix = datetime.now().strftime("%Y-%m-%d")
        phase_path = phase_dir / f"{date_prefix}-{normalize_slug(args.phase_slug)}.md"
        phase_output = build_phase_summary(args.title, compacted)

    if args.dry_run:
        print(
            f"Would compact {len(compacted)} entries, keep {len(retained)} recent entries,"
            f" update {log_path.name}{f', and write {phase_path.name}' if phase_path else ''}."
        )
        return 0

    log_path.write_text(new_text, encoding="utf-8")
    if phase_path is not None:
        phase_path.write_text(phase_output, encoding="utf-8")
        print(phase_path)
    print(log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
