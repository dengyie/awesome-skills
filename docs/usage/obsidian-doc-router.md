# Obsidian Doc Router Guide

`obsidian-doc-router` is a documentation routing and maintenance skill for personal/team Obsidian knowledge bases. It prevents LLMs from hallucinating ops facts or picking stale historical debug logs, and establishes an **anti-orphan documentation workflow**.

[Skill Matrix](skill-matrix.md) · [Quickstart](quickstart.md) · [Chinese Guide](../zh/README.zh-CN.md)

---

## When to Use

- Answering questions about VPS, server deployments, proxy gateways, tunnels, backups, domains, and topologies.
- Querying personal or team Obsidian vault notes without guessing from stale context memory.
- Writing, documenting, or refactoring infra/ops guides so newly created documents are never lost.

## Core Capabilities

1. **Deterministic Reading Path (two-tier router)**:
   - `.local/bin/doc-lookup "<query>"` merges the main table (`00.MOC/AI-DOC-ROUTER.md`, high-frequency compressed quick reference) with the six domain sub-routers under `00.MOC/routers/` (`ai-gateway`, `vps-network`, `infra-services`, `projects`, `knowledge-docs`, `accounts`, holding the full verbatim rows) -> Canonical Entry note -> Main handbook.
   - Hard budgets enforced by the scanner: main table ≤60 rows, ≤40,000 bytes, ≤15 triggers per row, ≤200 chars per quick cell; long changelogs live in `00.MOC/生产变更速记.md`, never back in the main table.
2. **Anti-Orphan Doc Recording**:
   - Standardized pathing under `Note/Infra/`, `Note/Project/`, or `Note/AI/经验/` (never non-existent dirs).
   - Governance metadata triplet (`doc_type` / `authority` / `lifecycle`; canonical also requires `canonical_for` + `scope`), plus `updated` and `aliases`.
   - Standardized structure with a `## 速读（当前有效 · 维护于 YYYY-MM-DD）` summary section (the header format is a parsing contract for `doc-lookup` and `scan-stale-docs --strict-tldr`).
   - Mandatory two-way mounting: full row into the matching sub-router, compressed quick row into the main table when high-frequency, plus MOC index links.
3. **Automated Consistency Check**:
   - Runs `python3 .local/bin/scan-doc-governance --strict` and `python3 .local/bin/scan-stale-docs --strict-status --strict-tldr` after changes; both must end with `RESULT=OK`.

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
