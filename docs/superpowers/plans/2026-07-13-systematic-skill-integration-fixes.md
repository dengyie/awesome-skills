# Systematic Skill Integration Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully publish the seventh skill package and prevent documentation paths from being misclassified as database migrations.

**Architecture:** Repository discovery tests derive the actual package set from top-level `SKILL.md` files and compare it with the documented catalog. Production review stack detection uses one shared path predicate for explicit database files and recognized migration directory segments.

**Tech Stack:** Markdown, YAML metadata, Python 3 standard-library `unittest`, Git.

## Global Constraints

- Work only in `fix/systematic-skill-integration`; keep the primary `main` worktree unchanged.
- Write failing regression evidence before production or documentation fixes.
- Do not redesign the behavior of any existing skill.
- Keep genuine `.sql`, `.sqlite`, `schema.prisma`, `migration/`, and `migrations/` paths classified as database work.
- Do not classify an ordinary file named `migration.md` as database work.

---

### Task 1: Narrow Database Stack Detection

**Files:**
- Modify: `production-code-quality-review/tests/test_review_skill_lib.py`
- Modify: `production-code-quality-review/scripts/review_skill_lib.py:227-250`
- Modify: `production-code-quality-review/scripts/review_skill_lib.py:802-829`

**Interfaces:**
- Consumes: repository-relative POSIX path strings.
- Produces: `is_database_path(path: str) -> bool`, used by `detect_stack()`, `derive_risk_flags()`, and `select_repo_stack_markers()`.

- [ ] **Step 1: Add failing regression tests**

Add these methods to `ReviewSkillLibTests`:

```python
def test_detect_stack_ignores_migration_documentation(self):
    module = load_module()

    result = module.detect_stack(["docs/superpowers/split-image-assets/migration.md"])

    self.assertNotIn("database", result["detected_stack"])
    self.assertNotIn("database.md", result["suggested_references"])

def test_select_repo_stack_markers_ignores_migration_documentation(self):
    module = load_module()

    markers = module.select_repo_stack_markers(
        [
            "docs/superpowers/split-image-assets/migration.md",
            "migrations/001_init.py",
            "database/schema.sql",
        ]
    )

    self.assertEqual(markers, ["migrations/001_init.py", "database/schema.sql"])

def test_risk_flags_ignore_migration_documentation(self):
    module = load_module()

    flags = module.derive_risk_flags(
        ["docs/superpowers/split-image-assets/migration.md"], diff_text=""
    )

    self.assertNotIn("database_migration", flags)
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  production-code-quality-review.tests.test_review_skill_lib.ReviewSkillLibTests.test_detect_stack_ignores_migration_documentation \
  production-code-quality-review.tests.test_review_skill_lib.ReviewSkillLibTests.test_select_repo_stack_markers_ignores_migration_documentation \
  production-code-quality-review.tests.test_review_skill_lib.ReviewSkillLibTests.test_risk_flags_ignore_migration_documentation -v
```

Expected: all three tests fail because `migration.md` currently selects the database stack, marker, and database-migration risk flag.

- [ ] **Step 3: Add the shared explicit predicate**

Add near `detect_stack()`:

```python
DATABASE_MIGRATION_DIR_NAMES = {"migration", "migrations"}


def is_database_path(path: str) -> bool:
    normalized = pathlib.PurePosixPath(normalize_repo_path(path).lower())
    return (
        normalized.suffix in {".sql", ".sqlite"}
        or normalized.name == "schema.prisma"
        or any(part in DATABASE_MIGRATION_DIR_NAMES for part in normalized.parts[:-1])
    )
```

Replace the database branch in `detect_stack()` with:

```python
if is_database_path(path):
    add_stack("database")
```

Replace the database condition in `derive_risk_flags()` with:

```python
if any(is_database_path(path) for path in paths):
    add_flag("database_migration")
```

Replace the broad marker clauses in `select_repo_stack_markers()` with:

```python
or is_database_path(path)
```

- [ ] **Step 4: Run focused and package tests and verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover production-code-quality-review/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

Expected: 50 production-review tests pass; clean-repository output does not include `database` or `database.md`.

- [ ] **Step 5: Commit the database fix**

```bash
git add production-code-quality-review/scripts/review_skill_lib.py \
  production-code-quality-review/tests/test_review_skill_lib.py
git commit -m "fix: narrow database migration detection"
```

### Task 2: Complete the Seventh Skill Package Contract

**Files:**
- Create: `codex-agent-worktree-setup/agents/openai.yaml`
- Create: `codex-agent-worktree-setup/tests/test_skill_package.py`
- Create: `docs/usage/codex-agent-worktree-setup.md`
- Modify: `tests/test_repository_docs.py`
- Modify: `README.md`
- Modify: `docs/usage/quickstart.md`
- Modify: `docs/usage/skill-matrix.md`
- Modify: `docs/zh/README.zh-CN.md`
- Modify: `docs/zh/quickstart.zh-CN.md`

**Interfaces:**
- Consumes: top-level directories containing `SKILL.md`.
- Produces: `DISCOVERED_SKILLS`, the actual repository package set used to verify the documented catalog.

- [ ] **Step 1: Make repository package discovery authoritative**

Replace the hard-coded `SKILLS` declaration in `tests/test_repository_docs.py` with:

```python
DISCOVERED_SKILLS = sorted(
    path.parent.name for path in ROOT.glob("*/SKILL.md") if path.parent.parent == ROOT
)

DOCUMENTED_SKILLS = [
    "best-project-memory",
    "codex-agent-worktree-setup",
    "evidence-driven-bugfix",
    "little-lighthouse-blog-publisher",
    "production-code-quality-review",
    "split-image-assets",
    "zero-to-website-design",
]
```

Add:

```python
def test_all_top_level_skills_are_in_the_documented_catalog(self):
    self.assertEqual(DISCOVERED_SKILLS, DOCUMENTED_SKILLS)
```

Update existing loops to iterate over `DOCUMENTED_SKILLS`. Add `docs/usage/codex-agent-worktree-setup.md` to `USAGE_GUIDES`.

- [ ] **Step 2: Add the package contract test before package assets**

Create `codex-agent-worktree-setup/tests/test_skill_package.py`:

```python
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class CodexAgentWorktreeSetupPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT.parent / "docs" / "usage" / "codex-agent-worktree-setup.md",
        ]
        missing = [str(path.relative_to(ROOT.parent)) for path in required_paths if not path.exists()]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: codex-agent-worktree-setup", frontmatter)
        self.assertIn("isolated branch-bound worktrees", frontmatter)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Codex Agent Worktree Setup"', metadata)
        self.assertIn("$codex-agent-worktree-setup", metadata)

    def test_main_worktree_and_detached_head_safety_are_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "Never develop directly in a primary `main` or `master` worktree.",
            "If the primary worktree has uncommitted changes, stop",
            "If the worktree is dirty, stop",
            "target branch is already checked out in another worktree",
        ]:
            self.assertIn(expected, skill_text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run repository and new package tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover codex-agent-worktree-setup/tests -v
```

Expected: failures report the missing usage guide and `agents/openai.yaml`, and landing pages do not contain `codex-agent-worktree-setup`.

- [ ] **Step 4: Add metadata and usage documentation**

Create `codex-agent-worktree-setup/agents/openai.yaml`:

```yaml
display_name: "Codex Agent Worktree Setup"
description: "Create and repair Codex-visible, branch-bound worktrees while protecting the primary main or master checkout."
trigger_phrases:
  - "$codex-agent-worktree-setup"
```

Create `docs/usage/codex-agent-worktree-setup.md` with these sections and concrete content:

```markdown
# Codex Agent Worktree Setup

Use `codex-agent-worktree-setup` when a Codex thread or development process needs its own branch-bound worktree, or when an existing Codex worktree is detached or incorrectly bound to the primary checkout.

## Best Fit
## Safety Boundaries
## Workflow
## Verification
## Prompt
## Related Docs
```

The guide must link to `[Skill Matrix](skill-matrix.md)` and `[Quickstart](quickstart.md)`, distinguish Git worktrees from Codex-visible threads, and include the primary-worktree, dirty-worktree, occupied-branch, and detached-HEAD guards from `SKILL.md`.

- [ ] **Step 5: Integrate the package into every public catalog**

Add `codex-agent-worktree-setup` to:

- the README skill table and repository layout;
- Quickstart package choices;
- Skill Matrix quick matrix, problem routing, expected-output routing, and prompt starters;
- Chinese overview count, skill list, selection table, and repository layout;
- Chinese Quickstart package choices.

Use this prompt starter consistently:

```text
Use $codex-agent-worktree-setup to create an isolated Codex worktree on the requested branch while keeping the primary main worktree unchanged.
```

- [ ] **Step 6: Run repository and package tests and verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover codex-agent-worktree-setup/tests -v
```

Expected: 8 repository tests and 3 new package tests pass.

- [ ] **Step 7: Commit the package integration**

```bash
git add README.md tests/test_repository_docs.py \
  codex-agent-worktree-setup/agents/openai.yaml \
  codex-agent-worktree-setup/tests/test_skill_package.py \
  docs/usage/codex-agent-worktree-setup.md \
  docs/usage/quickstart.md docs/usage/skill-matrix.md \
  docs/zh/README.zh-CN.md docs/zh/quickstart.zh-CN.md
git commit -m "docs: fully integrate worktree setup skill"
```

### Task 3: Full Regression Verification

**Files:**
- Verify: all files changed by Tasks 1 and 2.

**Interfaces:**
- Consumes: completed fixes from Tasks 1 and 2.
- Produces: fresh completion evidence and a clean feature worktree.

- [ ] **Step 1: Run every repository test suite**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover best-project-memory/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover codex-agent-worktree-setup/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover evidence-driven-bugfix/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover little-lighthouse-blog-publisher/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover production-code-quality-review/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover split-image-assets/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover zero-to-website-design/tests -v
```

Expected: 388 tests pass with zero failures.

- [ ] **Step 2: Run structural and direct symptom checks**

```bash
git diff --check main...HEAD
PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q \
  best-project-memory production-code-quality-review split-image-assets
PYTHONDONTWRITEBYTECODE=1 python3 production-code-quality-review/scripts/collect-review-context.py --repo .
git status --short --branch
git -C /Users/mango/project/awesome-skills/dengyie-awesome-skills status --short --branch
```

Expected: no whitespace or syntax errors; context output excludes `database` and `database.md`; primary worktree remains clean on `main`.

- [ ] **Step 3: Remove generated bytecode and confirm final status**

Delete only `__pycache__/*.pyc` files generated by the preceding compile command, remove empty generated `__pycache__` directories, and run:

```bash
git status --short --branch
git log --oneline --decorate -4
```

Expected: feature worktree has no uncommitted changes and contains the design plus two implementation commits.
