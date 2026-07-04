TASK_TYPE_CANDIDATE_LIFECYCLE = "candidate-lifecycle"
TASK_TYPE_PROVIDER_BRIDGE = "provider-bridge"
ALLOWED_TASK_TYPES = {
    TASK_TYPE_CANDIDATE_LIFECYCLE,
    TASK_TYPE_PROVIDER_BRIDGE,
}
SHARED_TASK_PROTOCOL_VERSION = "1.0"
SHARED_TASK_CONTRACT_REFERENCE = "split-image-assets/references/shared-task-contract.md"

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
        "task_goal": "record-compare-winner",
        "default_variant_id": "selection-only",
        "allowed_variant_ids": [
            "selection-only",
            "selection-then-promote-yes",
            "selection-then-decline",
        ],
    },
    (TASK_TYPE_CANDIDATE_LIFECYCLE, TASK_PHASE_CANDIDATE_PROMOTION, "record-candidate-promotion-approval"): {
        "task_goal": "decide-candidate-promotion",
        "default_variant_id": "approve-and-promote",
        "allowed_variant_ids": [
            "approve-and-promote",
            "decline-promotion",
        ],
    },
    (TASK_TYPE_PROVIDER_BRIDGE, TASK_PHASE_PROVIDER_BRIDGE, "prepare-generation-brief"): {
        "task_goal": "prepare-generation-brief",
        "default_variant_id": "prepare-generation-brief",
        "allowed_variant_ids": ["prepare-generation-brief"],
    },
    (TASK_TYPE_PROVIDER_BRIDGE, TASK_PHASE_PROVIDER_BRIDGE, "prepare-provider-request"): {
        "task_goal": "prepare-provider-request",
        "default_variant_id": "prepare-provider-request",
        "allowed_variant_ids": ["prepare-provider-request"],
    },
    (TASK_TYPE_PROVIDER_BRIDGE, TASK_PHASE_PROVIDER_BRIDGE, "await-provider-result"): {
        "task_goal": "await-provider-result",
        "default_variant_id": "record-provider-result",
        "allowed_variant_ids": ["record-provider-result"],
    },
    (TASK_TYPE_PROVIDER_BRIDGE, TASK_PHASE_PROVIDER_BRIDGE, "consume-provider-result"): {
        "task_goal": "consume-provider-result",
        "default_variant_id": "consume-provider-result",
        "allowed_variant_ids": ["consume-provider-result"],
    },
}
