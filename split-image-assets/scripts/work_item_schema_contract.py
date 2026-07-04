TASK_TYPE_CANDIDATE_LIFECYCLE = "candidate-lifecycle"
TASK_TYPE_PROVIDER_BRIDGE = "provider-bridge"
ALLOWED_TASK_TYPES = {
    TASK_TYPE_CANDIDATE_LIFECYCLE,
    TASK_TYPE_PROVIDER_BRIDGE,
}
SHARED_TASK_PROTOCOL_VERSION = "1.0"
SHARED_TASK_CONTRACT_REFERENCE = "split-image-assets/references/shared-task-contract.md"
SHARED_TASK_REGISTRY_VERSION = "1.0"
SHARED_TASK_REGISTRY_REFERENCE = "split-image-assets/scripts/work_item_schema_contract.py"

TASK_PHASE_CANDIDATE_SELECTION = "candidate-selection"
TASK_PHASE_CANDIDATE_PROMOTION = "candidate-promotion"
TASK_PHASE_PROVIDER_BRIDGE = "provider-bridge"
ALLOWED_TASK_PHASES = {
    TASK_PHASE_CANDIDATE_SELECTION,
    TASK_PHASE_CANDIDATE_PROMOTION,
    TASK_PHASE_PROVIDER_BRIDGE,
}

BRANCH_FLAG_PROMOTION_ANSWER = "promotion_answer"
BRANCH_FLAG_DECISION_ANSWER = "decision_answer"
BRANCH_FLAG_NEXT_ACTION = "next_action"
ALLOWED_BRANCH_FLAGS = {
    BRANCH_FLAG_PROMOTION_ANSWER,
    BRANCH_FLAG_DECISION_ANSWER,
    BRANCH_FLAG_NEXT_ACTION,
}

INTENT_RECORD_SELECTION_ONLY = "record-selection-only"
INTENT_RECORD_SELECTION_AND_PROMOTE = "record-selection-and-promote"
INTENT_RECORD_SELECTION_AND_DECLINE_PROMOTION = "record-selection-and-decline-promotion"
INTENT_APPROVE_AND_PROMOTE = "approve-and-promote"
INTENT_DECLINE_PROMOTION = "decline-promotion"
INTENT_PREPARE_GENERATION_BRIEF = "prepare-generation-brief"
INTENT_PREPARE_PROVIDER_REQUEST = "prepare-provider-request"
INTENT_RECORD_PROVIDER_RESULT = "record-provider-result"
INTENT_CONSUME_PROVIDER_RESULT = "consume-provider-result"
ALLOWED_INTENTS = {
    INTENT_RECORD_SELECTION_ONLY,
    INTENT_RECORD_SELECTION_AND_PROMOTE,
    INTENT_RECORD_SELECTION_AND_DECLINE_PROMOTION,
    INTENT_APPROVE_AND_PROMOTE,
    INTENT_DECLINE_PROMOTION,
    INTENT_PREPARE_GENERATION_BRIEF,
    INTENT_PREPARE_PROVIDER_REQUEST,
    INTENT_RECORD_PROVIDER_RESULT,
    INTENT_CONSUME_PROVIDER_RESULT,
}

TASK_REGISTRY = {
    (TASK_TYPE_CANDIDATE_LIFECYCLE, TASK_PHASE_CANDIDATE_SELECTION, "await-candidate-selection"): {
        "registry_key": "candidate-lifecycle.await-candidate-selection",
        "task_goal": "record-compare-winner",
        "default_variant_id": "selection-only",
        "allowed_variant_ids": [
            "selection-only",
            "selection-then-promote-yes",
            "selection-then-decline",
        ],
    },
    (TASK_TYPE_CANDIDATE_LIFECYCLE, TASK_PHASE_CANDIDATE_PROMOTION, "record-candidate-promotion-approval"): {
        "registry_key": "candidate-lifecycle.record-candidate-promotion-approval",
        "task_goal": "decide-candidate-promotion",
        "default_variant_id": "approve-and-promote",
        "allowed_variant_ids": [
            "approve-and-promote",
            "decline-promotion",
        ],
    },
    (TASK_TYPE_PROVIDER_BRIDGE, TASK_PHASE_PROVIDER_BRIDGE, "prepare-generation-brief"): {
        "registry_key": "provider-bridge.prepare-generation-brief",
        "task_goal": "prepare-generation-brief",
        "default_variant_id": "prepare-generation-brief",
        "allowed_variant_ids": ["prepare-generation-brief"],
    },
    (TASK_TYPE_PROVIDER_BRIDGE, TASK_PHASE_PROVIDER_BRIDGE, "prepare-provider-request"): {
        "registry_key": "provider-bridge.prepare-provider-request",
        "task_goal": "prepare-provider-request",
        "default_variant_id": "prepare-provider-request",
        "allowed_variant_ids": ["prepare-provider-request"],
    },
    (TASK_TYPE_PROVIDER_BRIDGE, TASK_PHASE_PROVIDER_BRIDGE, "await-provider-result"): {
        "registry_key": "provider-bridge.await-provider-result",
        "task_goal": "await-provider-result",
        "default_variant_id": "record-provider-result",
        "allowed_variant_ids": ["record-provider-result"],
    },
    (TASK_TYPE_PROVIDER_BRIDGE, TASK_PHASE_PROVIDER_BRIDGE, "consume-provider-result"): {
        "registry_key": "provider-bridge.consume-provider-result",
        "task_goal": "consume-provider-result",
        "default_variant_id": "consume-provider-result",
        "allowed_variant_ids": ["consume-provider-result"],
    },
}


def list_task_registry_entries() -> list[dict]:
    entries: list[dict] = []
    for (task_type, task_phase, task_state), registration in TASK_REGISTRY.items():
        entries.append(
            {
                "task_type": str(task_type),
                "task_phase": str(task_phase),
                "task_state": str(task_state),
                "registry_key": str(registration.get("registry_key", "")).strip(),
                "task_goal": str(registration.get("task_goal", "")).strip(),
                "default_variant_id": str(registration.get("default_variant_id", "")).strip(),
                "allowed_variant_ids": list(registration.get("allowed_variant_ids", [])),
            }
        )
    return entries


def validate_task_registry_source() -> list[str]:
    errors: list[str] = []
    entries = list_task_registry_entries()
    seen_registry_keys: set[str] = set()
    for entry in entries:
        registry_key = entry["registry_key"]
        if not registry_key:
            errors.append("registry entry must declare a non-empty registry_key")
        elif registry_key in seen_registry_keys:
            errors.append(f"duplicate registry_key: {registry_key}")
        else:
            seen_registry_keys.add(registry_key)
        if not entry["task_goal"]:
            errors.append(f"{registry_key or '<missing>'}: task_goal must be non-empty")
        default_variant_id = entry["default_variant_id"]
        if not default_variant_id:
            errors.append(f"{registry_key or '<missing>'}: default_variant_id must be non-empty")
        allowed_variant_ids = entry["allowed_variant_ids"]
        if not isinstance(allowed_variant_ids, list) or not allowed_variant_ids:
            errors.append(f"{registry_key or '<missing>'}: allowed_variant_ids must be a non-empty list")
            continue
        normalized_allowed_variant_ids: list[str] = []
        seen_variant_ids: set[str] = set()
        for item in allowed_variant_ids:
            if not isinstance(item, str) or not item.strip():
                errors.append(f"{registry_key or '<missing>'}: allowed_variant_ids entries must be non-empty strings")
                continue
            candidate = item.strip()
            if candidate in seen_variant_ids:
                errors.append(f"{registry_key or '<missing>'}: duplicate allowed_variant_id {candidate}")
                continue
            seen_variant_ids.add(candidate)
            normalized_allowed_variant_ids.append(candidate)
        if default_variant_id and default_variant_id not in normalized_allowed_variant_ids:
            errors.append(
                f"{registry_key or '<missing>'}: default_variant_id must appear in allowed_variant_ids"
            )
    return errors
