# Examples

## Example: Collect Review Context

Command:

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

Representative output shape:

```json
{
  "base": "origin/main",
  "changed_files": [
    "src/auth/session.ts",
    "migrations/002_add_accounts.sql"
  ],
  "changed_line_ranges": {
    "src/auth/session.ts": {
      "added": [{"start": 12, "end": 20}],
      "deleted": [{"start": 11, "end": 13}]
    }
  },
  "detected_stack": ["typescript", "node", "database"],
  "risk_flags": ["auth_or_access_control", "database_migration"],
  "suggested_references": [
    "review-framework.md",
    "output-contract.md",
    "false-positive-control.md",
    "security.md",
    "backend-and-integrations.md",
    "database.md",
    "verification-and-operations.md"
  ]
}
```

## Example: Generate Review Brief

Command:

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

Representative output shape:

```md
# Review Brief

## Scope
- Base: `origin/main`
- Scope mode: `working_tree`
- Changed files: `src/auth/session.ts`, `migrations/002_add_accounts.sql`

## Routing
- Review mode: `specialist`
- Reviewer set: `correctness`, `architecture`, `reliability`, `security`, `tests`

## Risk Flags
- `auth_or_access_control`
- `database_migration`

## Suggested References
- `review-framework.md`
- `output-contract.md`
- `false-positive-control.md`
- `security.md`
- `backend-and-integrations.md`
- `database.md`
```

## Example: Codex Prompt

Prompt:

```text
Use $production-code-quality-review to review this diff for production correctness, reliability, and merge readiness. Focus on introduced issues, not style.
```

## Example: Fast Verification

Command:

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```

Expected result:

- test suite completes successfully
- deterministic helper behavior remains intact
