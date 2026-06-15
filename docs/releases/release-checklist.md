# Release Checklist

Use this checklist before creating a new release for `production-code-quality-review`.

## 1. Verify Core Behavior

Run:

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```

Confirm:

- all tests pass
- fixture-style scenarios still behave as expected

## 2. Verify Main Entry Points

Run:

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
python3 production-code-quality-review/scripts/run-safe-checks.py --repo .
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
bash production-code-quality-review/scripts/verify-release.sh
```

Confirm:

- JSON output is structurally sane
- safe check suggestions are present
- markdown brief remains readable and useful
- bundled verification script completes successfully

## 3. Verify Docs

Check:

- `README.md`
- `docs/usage/quickstart.md`
- `docs/usage/review-workflows.md`
- `docs/usage/examples.md`
- `docs/usage/faq.md`
- `docs/usage/troubleshooting.md`

Confirm:

- paths are current
- commands are valid
- wording matches the actual repo structure

## 4. Update Release Notes

Update:

- `CHANGELOG.md`
- `docs/releases/<version>.md`

Confirm:

- highlights match the real diff
- breaking or notable changes are explicit

## 5. Verify Git State

Run:

```bash
git status --short
git log --oneline -1
```

Confirm:

- only intended changes are present
- final commit message is intentional

## 6. Publish

Run:

```bash
git push origin <branch>
gh release create <tag> --repo dengyie/awesome-skills --title "<title>" --notes-file docs/releases/<version>.md
```

After publishing:

- verify the release page renders correctly
- verify the remote branch is in sync
