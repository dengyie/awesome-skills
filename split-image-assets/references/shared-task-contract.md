# Shared Task Contract

Use this reference when reading or extending task-like recommendation surfaces such as:

- `_staging/repair_candidates/candidate_work_items.json`
- `_staging/providers/provider_work_items.json`

These surfaces still expose shell commands, but they now share a repo-owned recommendation contract so agents and downstream tooling do not have to infer everything from prose.

## Compatibility Layer

Every work-item entry may still expose:

- `recommended_command`

This remains the compatibility/default command string for older consumers.

## Branch Layer

When a state has meaningful alternatives, the work item may also expose:

- `recommended_command_variants[]`

Each variant should include:

- `variant_id`
- `phase`
- `label`
- `intent`
- `command`
- `note`
- `branch_flag`
- `branch_value`
- `recommended`
- `requires_fields[]`
- `writes_fields[]`
- `next_action_if_success`
- `requires_human_confirmation`

Protocol invariants:

- `variant_id`, `phase`, `intent`, `branch_flag`, and `branch_value` must be non-empty
- `phase`, `intent`, and `branch_flag` should come from `work_item_schema_contract.py`
- `requires_fields[]` and `writes_fields[]` should contain unique non-empty strings

## Task Layer

When variants belong to one coherent step family, the work item may also expose:

- `recommended_task`

That task object should include:

- `task_type`
- `task_phase`
- `task_state`
- `task_goal`
- `default_variant_id`
- `variant_count`
- `variants[]`
- `task_protocol_version`
- `task_contract_reference`
- `task_registry_version`
- `task_registry_reference`

`recommended_task.variants[]` should mirror the same variant objects already emitted in `recommended_command_variants[]`.

Protocol invariants:

- `variants[]` must be non-empty when `recommended_task` exists
- exactly one variant in that task should have `recommended=true`
- `default_variant_id` must match that recommended variant
- In plain terms: default_variant_id must match the one recommended branch.
- every variant inside one task should share the same `phase` as `task_phase`

## Shared Vocabulary

The canonical shared constants currently live in:

- `split-image-assets/scripts/work_item_schema_contract.py`

Current protocol identity:

- `task_protocol_version`: `1.0`
- `task_contract_reference`: `split-image-assets/references/shared-task-contract.md`
- `task_registry_version`: `1.0`
- `task_registry_reference`: `split-image-assets/scripts/work_item_schema_contract.py`

Each registered task should also expose a stable `task_registry_key`, for example:

- `candidate-lifecycle.await-candidate-selection`
- `candidate-lifecycle.record-candidate-promotion-approval`
- `provider-bridge.prepare-generation-brief`

The contract source should also be self-checked through:

- `list_task_registry_entries()`
- `validate_task_registry_source()`

The canonical shared builders currently live in:

- `split-image-assets/scripts/work_item_schema_lib.py`

The canonical registry accessors now include:

- `lookup_registered_task(...)`
- `lookup_registered_task_by_key(...)`
- `list_registered_tasks()`

Do not duplicate task-type, phase, branch-flag, or common intent literals in new code when these helpers already own them.

## Current Task Types

- `candidate-lifecycle`
- `provider-bridge`

## Current Task Phases

- `candidate-selection`
- `candidate-promotion`
- `provider-bridge`

## Current Branch Flags

- `promotion_answer`
- `decision_answer`
- `next_action`

## Current Shared Intents

- `record-selection-only`
- `record-selection-and-promote`
- `record-selection-and-decline-promotion`
- `approve-and-promote`
- `decline-promotion`
- `prepare-generation-brief`
- `prepare-provider-request`
- `record-provider-result`
- `consume-provider-result`

## Contract Rules

- Keep `recommended_command` even when richer fields exist.
- Add shared task metadata only when it describes a real workflow branch or grouped task.
- Prefer shared builders/constants over hand-built dicts and literals.
- Evolve candidate and provider work-item surfaces through this shared contract before adding a broader execution engine.
