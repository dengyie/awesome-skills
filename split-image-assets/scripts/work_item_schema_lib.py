from work_item_schema_contract import (
    ALLOWED_BRANCH_FLAGS,
    ALLOWED_INTENTS,
    ALLOWED_TASK_PHASES,
    ALLOWED_TASK_TYPES,
)


def _require_non_empty_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _normalize_string_list(values: list[str] | None, field_name: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values or []:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name} entries must be non-empty strings")
        candidate = item.strip()
        if candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    return normalized


def build_command_variant(
    variant_id: str,
    label: str,
    command: str,
    note: str = "",
    *,
    phase: str,
    intent: str,
    branch_flag: str,
    branch_value: str,
    recommended: bool,
    requires_fields: list[str] | None = None,
    writes_fields: list[str] | None = None,
    next_action_if_success: str = "",
    requires_human_confirmation: bool = False,
) -> dict:
    variant_id_value = _require_non_empty_string(variant_id, "variant_id")
    label_value = _require_non_empty_string(label, "label")
    command_value = _require_non_empty_string(command, "command")
    phase_value = _require_non_empty_string(phase, "phase")
    intent_value = _require_non_empty_string(intent, "intent")
    branch_flag_value = _require_non_empty_string(branch_flag, "branch_flag")
    branch_value_value = _require_non_empty_string(branch_value, "branch_value")
    if phase_value not in ALLOWED_TASK_PHASES:
        raise ValueError(f"phase must be one of: {sorted(ALLOWED_TASK_PHASES)}")
    if intent_value not in ALLOWED_INTENTS:
        raise ValueError(f"intent must be one of: {sorted(ALLOWED_INTENTS)}")
    if branch_flag_value not in ALLOWED_BRANCH_FLAGS:
        raise ValueError(f"branch_flag must be one of: {sorted(ALLOWED_BRANCH_FLAGS)}")
    if not isinstance(recommended, bool):
        raise ValueError("recommended must be a bool")
    return {
        "variant_id": variant_id_value,
        "phase": phase_value,
        "label": label_value,
        "intent": intent_value,
        "command": command_value,
        "note": note.strip() if isinstance(note, str) else "",
        "branch_flag": branch_flag_value,
        "branch_value": branch_value_value,
        "recommended": recommended,
        "requires_fields": _normalize_string_list(requires_fields, "requires_fields"),
        "writes_fields": _normalize_string_list(writes_fields, "writes_fields"),
        "next_action_if_success": next_action_if_success.strip()
        if isinstance(next_action_if_success, str)
        else "",
        "requires_human_confirmation": requires_human_confirmation,
    }


def build_recommended_task(
    *,
    task_type: str,
    task_phase: str,
    task_state: str,
    task_goal: str,
    default_variant_id: str,
    variants: list[dict],
) -> dict:
    task_type_value = _require_non_empty_string(task_type, "task_type")
    task_phase_value = _require_non_empty_string(task_phase, "task_phase")
    task_state_value = _require_non_empty_string(task_state, "task_state")
    task_goal_value = _require_non_empty_string(task_goal, "task_goal")
    default_variant_id_value = _require_non_empty_string(default_variant_id, "default_variant_id")
    if task_type_value not in ALLOWED_TASK_TYPES:
        raise ValueError(f"task_type must be one of: {sorted(ALLOWED_TASK_TYPES)}")
    if task_phase_value not in ALLOWED_TASK_PHASES:
        raise ValueError(f"task_phase must be one of: {sorted(ALLOWED_TASK_PHASES)}")
    if not isinstance(variants, list) or not variants:
        raise ValueError("variants must be a non-empty list")
    variant_ids: list[str] = []
    recommended_ids: list[str] = []
    normalized_variants: list[dict] = []
    for item in variants:
        if not isinstance(item, dict):
            raise ValueError("variants entries must be objects")
        variant_id = _require_non_empty_string(str(item.get("variant_id", "")), "variant.variant_id")
        variant_phase = _require_non_empty_string(str(item.get("phase", "")), "variant.phase")
        if variant_phase != task_phase_value:
            raise ValueError("all variants in one task must share the same phase as task_phase")
        if variant_id in variant_ids:
            raise ValueError("variant ids within one task must be unique")
        variant_ids.append(variant_id)
        if item.get("recommended") is True:
            recommended_ids.append(variant_id)
        normalized_variants.append(item)
    if default_variant_id_value not in variant_ids:
        raise ValueError("default_variant_id must match one of the provided variants")
    if len(recommended_ids) != 1:
        raise ValueError("exactly one variant per task must be marked recommended")
    if recommended_ids[0] != default_variant_id_value:
        raise ValueError("default_variant_id must match the recommended variant")
    return {
        "task_type": task_type_value,
        "task_phase": task_phase_value,
        "task_state": task_state_value,
        "task_goal": task_goal_value,
        "default_variant_id": default_variant_id_value,
        "variant_count": len(normalized_variants),
        "variants": normalized_variants,
    }
