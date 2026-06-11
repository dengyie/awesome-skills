# Codex Skills

Personal collection of reusable Codex skills.

## Skills

### production-code-quality-review

Evidence-first production code review SOP for pull requests, diffs, changed files, architecture-sensitive changes, production-readiness checks, reliability reviews, maintainability reviews, and merge-readiness decisions.

Use it when you want Codex to review code like a senior production engineer: focused on correctness, robustness, maintainability, architectural fit, scalability, observability, testability, and future evolution cost.

Path:

```text
production-code-quality-review/SKILL.md
```

## Repository Layout

Each skill lives in its own directory:

```text
skill-name/
  SKILL.md
  references/
  agents/
```

`SKILL.md` is the entry point. Optional `references/` files hold detailed checklists or supporting guidance, and optional `agents/` files hold agent-specific configuration.

## Install Locally

Copy a skill directory into your Codex skills directory:

```bash
cp -R production-code-quality-review ~/.codex/skills/
```

Then start a new Codex session or reload skills so Codex can discover it.

