# Task 1 Report: Rule And Contract Surface

## Outcome
Task 1 is complete.

I added the shared semantic-scope helper surface, re-exported it through the split-image-assets contract module, and tightened the package docs so they explicitly say global autonomy instructions do not by themselves satisfy semantic gates.

## What Changed
- Added `split-image-assets/scripts/semantic_scope_lib.py` with:
  - `ALLOWED_RESOURCE_FAMILIES`
  - `WEAK_AUTONOMY_EVIDENCE_MARKERS`
  - `default_scope_selection()`
  - `is_weak_autonomy_evidence(...)`
- Updated `split-image-assets/scripts/split_image_assets_contract.py` to re-export the new shared scope helpers.
- Updated the split-image-assets docs and references to say:
  - global autonomy instructions do not by themselves satisfy semantic gates
  - `inferred-from-user` must resolve the exact branch being recorded
  - `resource_family` belongs to the Granularity Alignment Gate / semantic narrowing surface
- Added failing-first tests in `split-image-assets/tests/test_docs_and_contract.py` and then made them pass.
- Refreshed `.codex-memory/` state, session history, decisions, and TODO tracking.

## Verification
Red phase:
- `python -B -m unittest split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_skill_docs_forbid_broad_autonomy_as_semantic_scope_evidence split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_shared_contract_exposes_resource_family_scope_fields`

Green phase:
- `python -B -m unittest split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_skill_docs_forbid_broad_autonomy_as_semantic_scope_evidence split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_shared_contract_exposes_resource_family_scope_fields`
- `python -B -m unittest split-image-assets.tests.test_docs_and_contract`

All verification passed.

## Commits
- `c1b7395` `feat: add semantic scope contract`
- `98f8dea` `chore: record task 1 handoff`

## Notes
- The working tree still has unrelated untracked files outside the Task 1 ownership set:
  - `.superpowers/`
  - `docs/superpowers/plans/2026-07-05-split-image-assets-granularity-gate-hardening.md`
  - `docs/superpowers/specs/2026-07-05-split-image-assets-granularity-gate-hardening-design.md`
- I left those alone.
