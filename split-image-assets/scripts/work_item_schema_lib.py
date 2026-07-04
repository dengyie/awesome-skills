from work_item_schema_contract import (
    ALLOWED_BRANCH_FLAGS,
    ALLOWED_INTENTS,
    ALLOWED_TASK_PHASES,
    ALLOWED_TASK_TYPES,
    SHARED_TASK_CONTRACT_REFERENCE,
    SHARED_TASK_PROTOCOL_VERSION,
    SHARED_TASK_REGISTRY_VERSION,
    TASK_REGISTRY,
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
    registration = TASK_REGISTRY.get((task_type_value, task_phase_value, task_state_value))
    if registration is None:
        raise ValueError("task_type/task_phase/task_state must match a registered shared task")
    registry_key = str(registration.get("registry_key", "")).strip()
    if not registry_key:
        raise ValueError("registered shared task must declare a non-empty registry_key")
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
    if task_goal_value != str(registration.get("task_goal", "")).strip():
        raise ValueError("task_goal must match the registered shared task goal")
    if default_variant_id_value != str(registration.get("default_variant_id", "")).strip():
        raise ValueError("default_variant_id must match the registered shared task default variant")
    allowed_variant_ids = registration.get("allowed_variant_ids", [])
    if not isinstance(allowed_variant_ids, list) or not all(
        isinstance(item, str) and item.strip() for item in allowed_variant_ids
    ):
        raise ValueError("registered shared task allowed_variant_ids must be a list of non-empty strings")
    unexpected_variant_ids = [item for item in variant_ids if item not in allowed_variant_ids]
    if unexpected_variant_ids:
        raise ValueError("variants must stay within the registered shared task variant ids")
    return {
        "task_protocol_version": SHARED_TASK_PROTOCOL_VERSION,
        "task_contract_reference": SHARED_TASK_CONTRACT_REFERENCE,
        "task_registry_version": SHARED_TASK_REGISTRY_VERSION,
        "task_registry_key": registry_key,
        "task_type": task_type_value,
        "task_phase": task_phase_value,
        "task_state": task_state_value,
        "task_goal": task_goal_value,
        "default_variant_id": default_variant_id_value,
        "variant_count": len(normalized_variants),
        "variants": normalized_variants,
    }


def build_recommendation_bundle(
    *,
    recommended_command: str = "",
    variants: list[dict] | None = None,
    task_type: str = "",
    task_phase: str = "",
    task_state: str = "",
    task_goal: str = "",
    default_variant_id: str = "",
) -> dict:
    command_value = recommended_command.strip() if isinstance(recommended_command, str) else ""
    normalized_variants = list(variants or [])
    recommended_task = None
    if normalized_variants:
        if not task_type or not task_phase or not task_state or not task_goal or not default_variant_id:
            raise ValueError(
                "task_type, task_phase, task_state, task_goal, and default_variant_id are required when variants are provided"
            )
        recommended_task = build_recommended_task(
            task_type=task_type,
            task_phase=task_phase,
            task_state=task_state,
            task_goal=task_goal,
            default_variant_id=default_variant_id,
            variants=normalized_variants,
        )
        if not command_value:
            command_value = str(recommended_task["variants"][0].get("command", "")).strip()
        default_variant = next(
            (
                item
                for item in recommended_task["variants"]
                if str(item.get("variant_id", "")).strip() == recommended_task["default_variant_id"]
            ),
            None,
        )
        if default_variant is None:
            raise ValueError("default variant could not be resolved from recommended_task")
        default_command = str(default_variant.get("command", "")).strip()
        if command_value != default_command:
            raise ValueError("recommended_command must match the default variant command when variants are provided")
    return {
        "recommended_command": command_value,
        "recommended_command_variants": normalized_variants,
        "recommended_task": recommended_task,
    }


def lookup_registered_task(
    *,
    task_type: str,
    task_phase: str,
    task_state: str,
) -> dict:
    task_type_value = _require_non_empty_string(task_type, "task_type")
    task_phase_value = _require_non_empty_string(task_phase, "task_phase")
    task_state_value = _require_non_empty_string(task_state, "task_state")
    registration = TASK_REGISTRY.get((task_type_value, task_phase_value, task_state_value))
    if registration is None:
        raise ValueError("task_type/task_phase/task_state must match a registered shared task")
    return {
        "task_type": task_type_value,
        "task_phase": task_phase_value,
        "task_state": task_state_value,
        "task_registry_version": SHARED_TASK_REGISTRY_VERSION,
        "task_registry_key": str(registration["registry_key"]),
        "task_goal": str(registration["task_goal"]),
        "default_variant_id": str(registration["default_variant_id"]),
        "allowed_variant_ids": list(registration["allowed_variant_ids"]),
    }
