# 示例

## 示例：收集 Review 上下文

命令：

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

典型输出结构：

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
  "risk_level": "high",
  "review_mode_reason": "high-risk change touches sensitive production surfaces",
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

## 示例：生成 Review 简报

命令：

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

典型输出结构：

```md
# Review Brief

## Scope
- Base: `origin/main`
- Scope mode: `working_tree`
- Changed files: `src/auth/session.ts`, `migrations/002_add_accounts.sql`

## Routing
- Review mode: `specialist`
- Risk level: `high`
- Why this mode: high-risk change touches sensitive production surfaces
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

## 示例：强制使用 PR 风格基线

命令：

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --base origin/main --scope branch --format compact
```

典型输出结构：

```text
review-mode=specialist risk-level=high changed-files=src/auth/session.ts,migrations/002_add_accounts.sql risk-flags=auth_or_access_control,database_migration refs=review-framework.md,output-contract.md,false-positive-control.md,security.md,backend-and-integrations.md,database.md,verification-and-operations.md
```

## 示例：Codex 提示词

提示词：

```text
Use $production-code-quality-review to review this diff for production correctness, reliability, and merge readiness. Focus on introduced issues, not style.
```

## 示例：快速验证

命令：

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```

预期结果：

- 测试全部通过
- deterministic helper 行为保持稳定
