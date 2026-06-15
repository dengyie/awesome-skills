# Golden Path

If you only do one thing, do this:

## 1. Install

```bash
bash production-code-quality-review/scripts/install-local-skill.sh
```

This installs to `~/.agents/skills` by default. Set `INSTALL_LEGACY_CODEX_COPY=1` only if you explicitly want a second legacy `~/.codex/skills` copy.
The installed copy keeps a source-checkout pointer so `update-local-skill.sh` can safely refresh it later.

## 2. Collect Context

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

## 3. Read The Compact Brief

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format compact
```

## 4. Ask Codex For The Review

```text
Use $production-code-quality-review to review this change for production correctness and merge readiness.
```

## 5. Verify

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```
