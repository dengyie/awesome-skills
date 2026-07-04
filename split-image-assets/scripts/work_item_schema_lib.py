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
    return {
        "variant_id": variant_id,
        "phase": phase,
        "label": label,
        "intent": intent,
        "command": command,
        "note": note,
        "branch_flag": branch_flag,
        "branch_value": branch_value,
        "recommended": recommended,
        "requires_fields": list(requires_fields or []),
        "writes_fields": list(writes_fields or []),
        "next_action_if_success": next_action_if_success,
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
    return {
        "task_type": task_type,
        "task_phase": task_phase,
        "task_state": task_state,
        "task_goal": task_goal,
        "default_variant_id": default_variant_id,
        "variant_count": len(variants),
        "variants": variants,
    }
