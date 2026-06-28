# Quickstart

Use this page when you want the shortest path from repository checkout to a working local skill install.

If you are still deciding which package to install, start with the [Skill Matrix](skill-matrix.md).

## 1. Choose one skill

Pick the package folder you actually need:

- `best-project-memory`
- `evidence-driven-bugfix`
- `little-lighthouse-blog-publisher`
- `production-code-quality-review`
- `split-image-assets`
- `zero-to-website-design`

Use the [Skill Matrix](skill-matrix.md) when the choice is unclear.

## 2. Install one skill

Current OpenAI Codex docs use:

- user scope: `$HOME/.agents/skills`
- repo scope: `.agents/skills`

Install one package by copying its folder:

```bash
mkdir -p ~/.agents/skills
cp -R <skill-folder> ~/.agents/skills/
```

Replace `<skill-folder>` with the package you chose, for example `evidence-driven-bugfix` or `zero-to-website-design`.

## 3. Reload Codex

After copying the folder:

- restart Codex, or
- reload skills in a fresh session

The goal is simply to make Codex rescan the installed skill directories.

## 4. Verify discovery

Open a new session and ask Codex to use the installed package directly, for example:

```text
Use $evidence-driven-bugfix to fix this failure by first capturing failing evidence and tracing the root cause.
```

If Codex recognizes the skill name, the install worked.

## 5. Go deeper

- Need help choosing: [Skill Matrix](skill-matrix.md)
- Want examples: [Examples](examples.md)
- Hit a problem: [Troubleshooting](troubleshooting.md)
- Prefer a guided repo walkthrough: [Golden Path](golden-path.md)
