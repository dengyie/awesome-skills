# Obsidian Doc Router Guide

`obsidian-doc-router` is a documentation routing and maintenance skill for personal/team Obsidian knowledge bases. It prevents LLMs from hallucinating ops facts or picking stale historical debug logs, and establishes an **anti-orphan documentation workflow**.

[Skill Matrix](skill-matrix.md) · [Quickstart](quickstart.md) · [Chinese Guide](../zh/README.zh-CN.md)

---

## When to Use

- Answering questions about VPS, server deployments, proxy gateways, tunnels, backups, domains, and topologies.
- Querying personal or team Obsidian vault notes without guessing from stale context memory.
- Writing, documenting, or refactoring infra/ops guides so newly created documents are never lost.

## Core Capabilities

1. **Deterministic Reading Path**:
   - `00.MOC/AI-DOC-ROUTER.md` (or `.local/bin/doc-lookup`) -> Canonical Entry note -> Main handbook.
2. **Anti-Orphan Doc Recording**:
   - Standardized pathing under `Note/Infra/`, `Note/Project/`, or `Note/AI/经验/` (never non-existent dirs).
   - Frontmatter metadata (`canonical`, `updated`, `aliases`).
   - Standardized structure with a `## 速读（当前有效 · 维护于 YYYY-MM-DD）` summary section (the header format is a parsing contract for `doc-lookup` and `scan-stale-docs --strict-tldr`).
   - Mandatory two-way link mounting back to `AI-DOC-ROUTER.md` and related MOC index files.
3. **Automated Consistency Check**:
   - Runs `python3 .local/bin/scan-stale-docs` after changes.

---

## Installation

```bash
mkdir -p ~/.agents/skills
cp -R obsidian-doc-router ~/.agents/skills/
```

Or for pi coding agent:
```bash
mkdir -p ~/.pi/agent/skills
cp -R obsidian-doc-router ~/.pi/agent/skills/
```
