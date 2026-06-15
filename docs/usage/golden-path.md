# Golden Path

If you only do one thing, do this:

## 1. Install

```bash
bash production-code-quality-review/scripts/install-local-skill.sh
```

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
