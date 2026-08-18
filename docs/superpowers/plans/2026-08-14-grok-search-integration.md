# Grok Search Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt the local `/Users/mango/.mirasim/skills/grok-search` package into Awesome Skills and make the repository copy the canonical maintenance source.

**Architecture:** Preserve the complete standalone Node.js skill package under `grok-search/`, then add only repository-owned integration metadata, package tests, and catalog documentation. Keep script behavior, skill instructions, tests, and user-facing documentation aligned around opt-in disclosure of fetched-content output paths.

**Tech Stack:** Node.js 18.17+, ECMAScript modules, Python `unittest`, Markdown, YAML

## Global Constraints

- Treat `/Users/mango/.mirasim/skills/grok-search` as the import source for this integration.
- Treat `grok-search/` in Awesome Skills as the canonical source after integration.
- Do not import `.git/`, `node_modules/`, credentials, generated output, or machine-local configuration.
- Preserve one JSON object on stdout for every script invocation.
- Expose fetched-content `full_path` only when `--full-path` is explicitly requested.

---

### Task 1: Import And Align The Skill Package

**Files:**
- Modify: `grok-search/scripts/fetch.js`
- Modify: `grok-search/tests/argv.test.js`
- Modify: `grok-search/SKILL.md`
- Modify: `grok-search/README.md`
- Modify: `grok-search/README.en.md`
- Modify: `grok-search/docs/features.md`
- Create: `grok-search/agents/openai.yaml`
- Create: `grok-search/tests/test_skill_package.py`

**Interfaces:**
- Consumes: `/Users/mango/.mirasim/skills/grok-search` package files, excluding `.git/` and `node_modules/`
- Produces: a self-contained `grok-search/` skill whose fetch result includes `content.full_path: string | null` only with `--full-path`

- [x] **Step 1: Capture the imported behavior with a regression test**

Update the long-content fetch test so the default command asserts `Object.hasOwn(output.content, "full_path") === false`, then run a second command with `--full-path` and assert that the referenced file contains 13,000 characters.

- [x] **Step 2: Verify the stale test fails against the imported implementation**

Run: `npm test`

Expected before the test correction: `tests/argv.test.js` fails while reading an undefined `content.full_path`.

- [x] **Step 3: Align skill instructions and package documentation**

Document that `--full-path` is opt-in for fetch results and that increasing `--max-chars` is the normal next step when the preview is insufficient. Keep search result `answer.full_path` and raw source `sources.raw_path` behavior unchanged.

- [x] **Step 4: Generate current Codex UI metadata**

Write `agents/openai.yaml` with an `interface` mapping containing:

```yaml
interface:
  display_name: "Grok Search"
  short_description: "Search and read the live web with sourced results"
  default_prompt: "Use $grok-search to find the current answer on the live web and cite the sources you relied on."
```

- [x] **Step 5: Verify package behavior and structure**

Run:

```bash
npm test
python3 -m unittest discover tests -v
python3 /Users/mango/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

Expected: all Node tests pass, all package tests pass, and skill validation reports `Skill is valid!`.

### Task 2: Wire Grok Search Into The Repository Catalog

**Files:**
- Modify: `README.md`
- Modify: `docs/usage/quickstart.md`
- Modify: `docs/usage/skill-matrix.md`
- Modify: `docs/zh/README.zh-CN.md`
- Modify: `docs/zh/quickstart.zh-CN.md`
- Create: `docs/usage/grok-search.md`
- Modify: `tests/test_repository_docs.py`

**Interfaces:**
- Consumes: the canonical `grok-search/` package and its `$grok-search` invocation name
- Produces: catalog routing, installation discovery, usage guidance, and link-integrity coverage

- [x] **Step 1: Add repository catalog coverage**

Add `grok-search` to `DOCUMENTED_SKILLS` and add `docs/usage/grok-search.md` to `USAGE_GUIDES` so a missing catalog entry or guide fails repository tests.

- [x] **Step 2: Add English and Chinese navigation entries**

List `grok-search` in both landing pages, both quickstarts, the repository layout, and the skill matrix. Route current-fact lookup, URL reading, and site discovery requests to this skill.

- [x] **Step 3: Publish the package usage guide**

Describe requirements, secure configuration, script routing, JSON result reading, provider limitations, `--full-path` opt-in behavior, verification commands, and a `$grok-search` prompt starter.

- [x] **Step 4: Run repository verification**

Run: `python3 -m unittest discover tests -v`

Expected: every repository documentation and link-integrity test passes.

- [x] **Step 5: Review the final integration diff**

Run:

```bash
git status --short
git diff --check
git diff --stat
```

Expected: all changes are scoped to the new `grok-search` package, its catalog wiring, its integration plan, and repository regression coverage; `git diff --check` emits no output.
