ALLOWED_PAUSE_CATEGORIES = {"user-decision", "external-blocker", "formal-approval"}
ALLOWED_BLOCKING_VALUES = {"true", "false"}
ALLOWED_DECISION_SOURCES = {
    "explicit-user-confirmed",
    "inferred-from-user",
}
ALLOWED_CONFIRMATION_STATUSES = {"pending", "confirmed", "not-required"}
ALLOWED_CONFIRMATION_SOURCES = {
    "explicit-user-confirmed",
    "inferred-from-user",
    "unset",
}
NON_DEFAULT_CONFIRMATION_SOURCES = {
    "explicit-user-confirmed",
    "inferred-from-user",
}
ALLOWED_QA_STATUSES = {"pass", "needs-review", "blocked"}
ALLOWED_QUALITY_CHECK_STATUSES = {"pass", "needs-review", "blocked", "unknown"}
ALLOWED_GRANULARITY_MODES = {
    "module",
    "component",
    "atomic-layer",
    "production-editable",
    "draft",
}
ALLOWED_SCOPE_STRATEGIES = {"high-signal-subset", "full-image-batch", "unset"}
ALLOWED_TEXT_HANDLING = {"extract-as-image", "rebuild-downstream", "unset"}
ALLOWED_CARRIER_GLYPH_POLICIES = {"split", "grouped", "conditional", "unset"}
ALLOWED_BACKGROUND_EXPECTATIONS = {"exact-recovery", "approximate-accepted", "unset"}
ALLOWED_LAYER_INDEPENDENCE = {"static-reuse", "animation-ready", "unset"}
ALLOWED_CAPABILITY_CHOICES = {
    "install-or-activate-tools",
    "external-professional-outputs",
    "draft-packaging-only",
    "production-capable",
    "unset",
}
ALLOWED_ASSET_CLASSES = {
    "atomic",
    "grouped-support",
    "background-support",
    "preview-reference",
    "candidate",
}
ALLOWED_REUSE_STATUSES = {
    "production-ready",
    "draft-candidate",
    "support-only",
    "blocked",
    "approximate-reconstruction",
}
ALLOWED_DELIVERY_CLASSES = {
    "clean-extraction",
    "approximate-reconstruction",
    "generated-reconstruction",
    "support-only",
    "draft-candidate",
}
ALLOWED_TEXT_ROLES = {
    "plain-text",
    "button-label",
    "numeric-value",
    "form-value",
    "logo-wordmark",
    "decorative-text",
    "non-text",
}
ORDINARY_TEXT_ROLES = {"plain-text", "button-label", "numeric-value", "form-value"}
ALLOWED_TEXT_RENDER_CLASSES = {
    "editable",
    "styled-editable",
    "visual-fidelity-critical",
    "non-text",
}
ALLOWED_SCORE_VALUES = {"unset", "low", "medium", "high"}
ALLOWED_ROUTING_ACTIONS = {
    "unset",
    "extract_asset",
    "rebuild_downstream",
    "requires_user_confirmation",
    "support_only",
}
ALLOWED_ROUTING_DECISION_SOURCES = {
    "unset",
    "explicit-user-confirmed",
    "inferred-from-user",
}
ALLOWED_OBJECT_TYPES = {
    "ui-carrier",
    "ui-glyph",
    "carrier-glyph-pair",
    "soft-edge-logo-brand-mark",
    "outlined-illustration-logo",
    "flat-support-plate",
    "grouped-support-plate",
    "photo-object-matte",
    "generic-object",
}
ALLOWED_QUALITY_TARGET_TIERS = {
    "structural-valid",
    "usable-draft",
    "visual-acceptance-ready",
}
ALLOWED_PLANNED_ROUTES = {
    "extract",
    "reconstruct",
    "generate",
    "rebuild_downstream",
    "support_only",
}
ROUTE_SIGNAL_KEYS = (
    "recoverability_low",
    "object_is_reconstruction_like",
    "quality_target_high",
    "segmentation_cost_unfavorable",
)
ALLOWED_GENERATION_PROVIDER_CLASSES = {
    "unset",
    "codex-controlled-generation",
    "external-generated-outputs",
    "local-model-runtime",
}
REQUIRED_CONFIRMATION_KEYS = {
    "tooling_preflight",
    "granularity_alignment",
    "generation_routing",
    "pilot_object",
    "approximate_reconstruction",
    "final_acceptance",
    "candidate_promotion",
}
STAGE_TO_CONFIRMATION_KEY = {
    "tooling-preflight": "tooling_preflight",
    "tooling_preflight": "tooling_preflight",
    "granularity-alignment": "granularity_alignment",
    "granularity_alignment": "granularity_alignment",
    "generation-routing": "generation_routing",
    "generation-routing-gate": "generation_routing",
    "generation_routing": "generation_routing",
    "pilot-object": "pilot_object",
    "pilot-object-gate": "pilot_object",
    "pilot_object": "pilot_object",
    "approximate-reconstruction-acceptance": "approximate_reconstruction",
    "approximate-reconstruction-acceptance-gate": "approximate_reconstruction",
    "approximate_reconstruction": "approximate_reconstruction",
    "reconstruction-acceptance": "approximate_reconstruction",
    "final-acceptance": "final_acceptance",
    "final_acceptance": "final_acceptance",
    "candidate-promotion-acceptance": "candidate_promotion",
    "candidate-promotion-acceptance-gate": "candidate_promotion",
    "candidate_promotion": "candidate_promotion",
    "final-promotion-acceptance": "candidate_promotion",
}
DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION = {
    "tooling_preflight": "external-blocker",
    "granularity_alignment": "user-decision",
    "generation_routing": "user-decision",
    "pilot_object": "formal-approval",
    "approximate_reconstruction": "user-decision",
    "final_acceptance": "formal-approval",
    "candidate_promotion": "formal-approval",
}


def default_confirmation_entry(key: str) -> dict:
    entry = {
        "status": "pending",
        "source": "unset",
        "pause_category": DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION.get(key, ""),
        "notes": "",
        "evidence_ref": "",
    }
    if key == "pilot_object":
        entry["object_id"] = ""
    return entry


def default_object_routing_fields() -> dict:
    return {
        "value_scoring": {
            "editability_score": "unset",
            "visual_complexity_score": "unset",
            "asset_value_score": "unset",
            "scoring_reason": "",
        },
        "decision_routing": {
            "recommended_action": "unset",
            "final_action": "unset",
            "decision_source": "unset",
        },
        "rebuild_intent": {
            "rebuildable_downstream": False,
            "rebuild_notes": "",
        },
        "text_semantics": {
            "text_role": "non-text",
            "text_render_class": "non-text",
        },
    }


def default_plan_manifest(source_path: str, package_name: str, width: int, height: int) -> dict:
    return {
        "schema_version": "1.0",
        "package_name": package_name,
        "source": {
            "path": "source/source_original.png",
            "original_path": source_path,
            "width": width,
            "height": height,
        },
        "quality_target": {
            "tier": "structural-valid",
            "notes": "",
        },
        "planning_status": {
            "status": "pending",
            "notes": "Whole-image planning has not been completed yet.",
        },
        "route_policy": {
            "planning_required": True,
            "generation_routing_gate": "pending",
            "plan_manifest_rollout_stage": "phase1-scaffold",
            "notes": "",
        },
        "provider_preferences": {
            "generation_provider_class": "unset",
            "segmentation_provider_class": "unset",
        },
        "objects": [],
        "batch_groups": [],
        "summary": {
            "planned_extract": 0,
            "planned_reconstruct": 0,
            "planned_generate": 0,
            "planned_rebuild_downstream": 0,
            "planned_support_only": 0,
        },
    }


def default_generation_brief(object_id: str = "", object_type: str = "generic-object") -> dict:
    return {
        "object_id": object_id,
        "object_type": object_type,
        "source_crop": "",
        "rough_localization": "",
        "rough_mask": "",
        "neighbor_context": "",
        "style_constraints": [],
        "must_keep": [],
        "must_avoid": [],
        "target_transparency": "tight-transparent-png",
        "intended_delivery_class": "generated-reconstruction",
        "why_not_extract": "",
        "why_not_reconstruct": "",
        "why_generate": "",
        "risk_note": "",
    }
