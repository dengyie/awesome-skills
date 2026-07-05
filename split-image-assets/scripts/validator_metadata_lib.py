from split_image_assets_contract import (
    ALLOWED_RESOURCE_FAMILIES,
    ALLOWED_BACKGROUND_EXPECTATIONS,
    ALLOWED_BLOCKING_VALUES,
    ALLOWED_CAPABILITY_CHOICES,
    ALLOWED_CARRIER_GLYPH_POLICIES,
    ALLOWED_CONFIRMATION_SOURCES,
    ALLOWED_CONFIRMATION_STATUSES,
    ALLOWED_DECISION_SOURCES,
    ALLOWED_GENERATION_PROVIDER_CLASSES,
    ALLOWED_GRANULARITY_MODES,
    ALLOWED_LAYER_INDEPENDENCE,
    ALLOWED_PAUSE_CATEGORIES,
    ALLOWED_QA_STATUSES,
    ALLOWED_QUALITY_TARGET_TIERS,
    ALLOWED_SCOPE_STRATEGIES,
    ALLOWED_TEXT_HANDLING,
    NON_DEFAULT_CONFIRMATION_SOURCES,
    REQUIRED_CONFIRMATION_KEYS,
)
from semantic_scope_lib import is_weak_autonomy_evidence
from validator_shared import (
    ALLOWED_AUDIT_CODES,
    REQUIRED_ASSET_SUMMARY_FIELDS,
    REQUIRED_DECISION_FIELDS,
    REQUIRED_NONEMPTY_DECISION_FIELDS,
    REQUIRED_PIPELINE_STAGES,
    decision_answer,
    has_affirmative_decision,
    is_ui_like_package,
    package_requires_extraction_capability_for_pass,
)


def validate_metadata_fields(metadata: dict, errors: list[str], plan_manifest: dict | None = None) -> None:
    for field in [
        "schema_version",
        "package_name",
        "source",
        "analysis",
        "extraction_pipeline",
        "objects",
        "asset_summary",
        "audit",
        "qa",
    ]:
        if field not in metadata:
            errors.append(f"metadata missing required field: {field}")
    source = metadata.get("source", {})
    if not isinstance(source, dict):
        errors.append("metadata.source must be an object")
        source = {}
    for field in ["path", "width", "height"]:
        if field not in source:
            errors.append(f"metadata.source missing required field: {field}")
    analysis = metadata.get("analysis", {})
    if not isinstance(analysis, dict):
        errors.append("metadata.analysis must be an object")
        analysis = {}
    visual_hierarchy = analysis.get("visual_hierarchy")
    if not isinstance(visual_hierarchy, list) or not visual_hierarchy:
        errors.append("metadata.analysis.visual_hierarchy must include a semantic visual hierarchy")
    split_plan = analysis.get("recommended_split_plan")
    if not isinstance(split_plan, str) or not split_plan.strip():
        errors.append("metadata.analysis.recommended_split_plan must describe semantic layer boundaries")
    granularity = metadata.get("granularity", {})
    if not isinstance(granularity, dict):
        errors.append("metadata.granularity must be an object")
        granularity = {}
    mode = granularity.get("mode")
    if mode not in ALLOWED_GRANULARITY_MODES:
        errors.append("metadata.granularity.mode must record the agreed split granularity")
    user_confirmed = granularity.get("user_confirmed")
    if not isinstance(user_confirmed, bool):
        errors.append("metadata.granularity.user_confirmed must be true or false")
    elif user_confirmed is not True:
        errors.append("metadata.granularity.user_confirmed must be true before validation")
    notes = granularity.get("notes")
    if not isinstance(notes, str):
        errors.append("metadata.granularity.notes must be a string")
    elif not notes.strip():
        errors.append("metadata.granularity.notes must explain the aligned split scope")
    for field_name, allowed in [
        ("scope_strategy", ALLOWED_SCOPE_STRATEGIES),
        ("text_handling", ALLOWED_TEXT_HANDLING),
        ("carrier_glyph_policy", ALLOWED_CARRIER_GLYPH_POLICIES),
        ("background_expectation", ALLOWED_BACKGROUND_EXPECTATIONS),
        ("layer_independence", ALLOWED_LAYER_INDEPENDENCE),
    ]:
        value = granularity.get(field_name, "unset")
        if value not in allowed:
            errors.append(f"metadata.granularity.{field_name} must be one of: {', '.join(sorted(allowed))}")
    resource_family = granularity.get("resource_family", "")
    if not isinstance(resource_family, str):
        errors.append("metadata.granularity.resource_family must be a string")
        resource_family = ""
    else:
        resource_family = resource_family.strip()
        if resource_family and resource_family not in ALLOWED_RESOURCE_FAMILIES:
            errors.append(
                "metadata.granularity.resource_family must be one of: "
                + ", ".join(sorted(ALLOWED_RESOURCE_FAMILIES))
            )
    resource_family_confirmed = granularity.get("resource_family_confirmed", False)
    if resource_family_confirmed not in {True, False}:
        errors.append("metadata.granularity.resource_family_confirmed must be true or false when present")
    resource_family_evidence_ref = granularity.get("resource_family_evidence_ref", "")
    if not isinstance(resource_family_evidence_ref, str):
        errors.append("metadata.granularity.resource_family_evidence_ref must be a string")
        resource_family_evidence_ref = ""
    scope_selection = plan_manifest.get("scope_selection", {}) if isinstance(plan_manifest, dict) else {}
    if not isinstance(scope_selection, dict):
        scope_selection = {}
    candidate_families = scope_selection.get("candidate_families", [])
    has_candidate_families = isinstance(candidate_families, list) and any(
        (
            isinstance(entry, str) and entry.strip()
        )
        or (
            isinstance(entry, dict)
            and isinstance(entry.get("family_id"), str)
            and entry.get("family_id", "").strip()
        )
        for entry in candidate_families
    )
    selected_family = str(scope_selection.get("selected_family", "")).strip()
    selection_source = str(scope_selection.get("selection_source", "unresolved")).strip() or "unresolved"
    selection_evidence_ref = str(scope_selection.get("selection_evidence_ref", "")).strip()
    requires_resource_family = (
        granularity.get("scope_strategy") == "high-signal-subset"
        and (
            is_ui_like_package(metadata)
            or has_candidate_families
            or bool(selected_family)
        )
    )
    if requires_resource_family and not resource_family:
        errors.append("granularity.resource_family is required for dense high-signal-subset packages")
        if not selected_family:
            errors.append("semantic-family narrowing is unresolved: plan_manifest.scope_selection.selected_family is empty")
    decision_log = metadata.get("decision_log", [])
    if not isinstance(decision_log, list):
        errors.append("metadata.decision_log must be a list")
    else:
        for index, entry in enumerate(decision_log):
            if not isinstance(entry, dict):
                errors.append(f"metadata.decision_log[{index}] must be an object")
                continue
            missing = sorted(REQUIRED_DECISION_FIELDS - set(entry))
            if "recorded_answer" not in entry and "user_answer" not in entry:
                missing.append("recorded_answer")
            if missing:
                errors.append(f"metadata.decision_log[{index}] missing required fields: " + ", ".join(missing))
            for field in REQUIRED_NONEMPTY_DECISION_FIELDS:
                value = entry.get(field)
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    errors.append(f"metadata.decision_log[{index}].{field} must be a non-empty string")
            evidence_ref = entry.get("evidence_ref")
            if evidence_ref is not None and not isinstance(evidence_ref, str):
                errors.append(f"metadata.decision_log[{index}].evidence_ref must be a string")
            if not decision_answer(entry):
                errors.append(f"metadata.decision_log[{index}].recorded_answer must be a non-empty string")
            decision_source = entry.get("decision_source")
            if decision_source not in ALLOWED_DECISION_SOURCES:
                errors.append(
                    f"metadata.decision_log[{index}].decision_source must be one of: "
                    + ", ".join(sorted(ALLOWED_DECISION_SOURCES))
                )
            pause_category = entry.get("pause_category")
            if pause_category not in ALLOWED_PAUSE_CATEGORIES:
                errors.append(
                    f"metadata.decision_log[{index}].pause_category must be one of: "
                    + ", ".join(sorted(ALLOWED_PAUSE_CATEGORIES))
                )
            blocking = entry.get("blocking")
            if blocking not in ALLOWED_BLOCKING_VALUES:
                errors.append(
                    f"metadata.decision_log[{index}].blocking must be one of: "
                    + ", ".join(sorted(ALLOWED_BLOCKING_VALUES))
                )
            if decision_source == "inferred-from-user":
                if not isinstance(evidence_ref, str) or not evidence_ref.strip():
                    errors.append(
                        f"metadata.decision_log[{index}].evidence_ref is required when decision_source=inferred-from-user"
                    )
    qa = metadata.get("qa", {})
    qa_status = qa.get("status") if isinstance(qa, dict) else None
    if qa_status == "pass" and not decision_log:
        errors.append("qa.status pass requires at least one decision_log entry documenting user acceptance")
    confirmation = metadata.get("confirmation", {})
    if not isinstance(confirmation, dict):
        errors.append("metadata.confirmation must be an object")
        confirmation = {}
    missing_confirmation = sorted(REQUIRED_CONFIRMATION_KEYS - set(confirmation))
    if missing_confirmation:
        errors.append("metadata.confirmation missing required gates: " + ", ".join(missing_confirmation))
    else:
        for key in REQUIRED_CONFIRMATION_KEYS:
            entry = confirmation.get(key)
            if not isinstance(entry, dict):
                errors.append(f"metadata.confirmation.{key} must be an object")
                continue
            status = entry.get("status")
            source = entry.get("source")
            notes = entry.get("notes")
            pause_category = entry.get("pause_category", "")
            evidence_ref = entry.get("evidence_ref", "")
            if status not in ALLOWED_CONFIRMATION_STATUSES:
                errors.append(
                    f"metadata.confirmation.{key}.status must be one of: "
                    + ", ".join(sorted(ALLOWED_CONFIRMATION_STATUSES))
                )
            if source not in ALLOWED_CONFIRMATION_SOURCES:
                errors.append(
                    f"metadata.confirmation.{key}.source must be one of: "
                    + ", ".join(sorted(ALLOWED_CONFIRMATION_SOURCES))
                )
            if not isinstance(notes, str):
                errors.append(f"metadata.confirmation.{key}.notes must be a string")
            if not isinstance(evidence_ref, str):
                errors.append(f"metadata.confirmation.{key}.evidence_ref must be a string")
            if status in {"confirmed", "not-required"}:
                if source not in NON_DEFAULT_CONFIRMATION_SOURCES:
                    errors.append(
                        f"metadata.confirmation.{key}.source must come from explicit-user-confirmed or inferred-from-user"
                    )
                if pause_category not in ALLOWED_PAUSE_CATEGORIES:
                    errors.append(
                        f"metadata.confirmation.{key}.pause_category must be one of: "
                        + ", ".join(sorted(ALLOWED_PAUSE_CATEGORIES))
                    )
                if source == "inferred-from-user" and not evidence_ref.strip():
                    errors.append(
                        f"metadata.confirmation.{key}.evidence_ref is required when source=inferred-from-user"
                    )
            if status == "pending" and source != "unset":
                errors.append(f"metadata.confirmation.{key}.source must be unset when status=pending")
            if key == "pilot_object":
                object_id = entry.get("object_id")
                if not isinstance(object_id, str):
                    errors.append("metadata.confirmation.pilot_object.object_id must be a string")
                elif status == "confirmed" and not object_id.strip():
                    errors.append(
                        "metadata.confirmation.pilot_object.object_id must be non-empty when the pilot gate is confirmed"
                    )
    if resource_family:
        granularity_alignment = confirmation.get("granularity_alignment", {}) if isinstance(confirmation, dict) else {}
        decision_source = ""
        evidence_ref = resource_family_evidence_ref
        if isinstance(granularity_alignment, dict):
            decision_source = str(granularity_alignment.get("source", "")).strip()
            if not evidence_ref:
                evidence_ref = str(granularity_alignment.get("evidence_ref", "")).strip()
        if selection_source == "inferred-from-user":
            decision_source = selection_source
            if not evidence_ref:
                evidence_ref = selection_evidence_ref
        if decision_source == "inferred-from-user":
            normalized_evidence = evidence_ref.strip().lower()
            normalized_family = resource_family.lower()
            if is_weak_autonomy_evidence(normalized_evidence) or normalized_family not in normalized_evidence:
                errors.append(
                    "inferred-from-user evidence must resolve the exact branch being recorded for resource_family"
                )
    asset_summary = metadata.get("asset_summary")
    if not isinstance(asset_summary, dict):
        errors.append("metadata.asset_summary must be an object")
        asset_summary = {}
    missing_summary = sorted(REQUIRED_ASSET_SUMMARY_FIELDS - set(asset_summary))
    if missing_summary:
        errors.append("metadata.asset_summary missing required fields: " + ", ".join(missing_summary))
    for field in REQUIRED_ASSET_SUMMARY_FIELDS & set(asset_summary):
        value = asset_summary.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errors.append(f"metadata.asset_summary.{field} must be a non-negative integer")
    audit = metadata.get("audit", {})
    if not isinstance(audit, dict):
        errors.append("metadata.audit must be an object")
    elif audit:
        quality_audit_path = audit.get("quality_audit_path")
        if not isinstance(quality_audit_path, str) or not quality_audit_path.strip():
            errors.append("metadata.audit.quality_audit_path must be a package-relative path")
        elif not quality_audit_path.startswith("_staging/") and not quality_audit_path.startswith("_archive_intermediate/"):
            errors.append("metadata.audit.quality_audit_path must stay in _staging/ or _archive_intermediate/")
        warning_codes = audit.get("warning_codes", [])
        if not isinstance(warning_codes, list) or not all(
            isinstance(code, str) and code in ALLOWED_AUDIT_CODES for code in warning_codes
        ):
            errors.append("metadata.audit.warning_codes must use the supported visual warning taxonomy")
    capability = metadata.get("capability", {})
    if not isinstance(capability, dict):
        errors.append("metadata.capability must be an object")
        capability = {}
    production_capable = capability.get("production_capable")
    if not isinstance(production_capable, bool):
        errors.append("metadata.capability.production_capable must be true or false")
    missing_for_production = capability.get("missing_for_production")
    if not isinstance(missing_for_production, list) or not all(
        isinstance(item, str) and item.strip() for item in missing_for_production
    ):
        errors.append("metadata.capability.missing_for_production must be a list of non-empty strings")
    user_choice = capability.get("user_choice")
    if user_choice not in ALLOWED_CAPABILITY_CHOICES:
        errors.append("metadata.capability.user_choice must record the tooling preflight decision")
    notes = capability.get("notes")
    if not isinstance(notes, str):
        errors.append("metadata.capability.notes must be a string")
    generation_capability = capability.get("generation")
    if generation_capability is not None and not isinstance(generation_capability, dict):
        errors.append("metadata.capability.generation must be an object when present")
        generation_capability = None
    qa_for_capability = metadata.get("qa", {})
    qa_status_for_capability = qa_for_capability.get("status") if isinstance(qa_for_capability, dict) else None
    if qa_status_for_capability == "pass" and user_choice == "unset":
        errors.append("metadata.capability.user_choice must not stay unset when qa.status=pass")
    if (
        qa_status_for_capability == "pass"
        and package_requires_extraction_capability_for_pass(metadata)
        and production_capable is not True
    ):
        errors.append(
            "qa.status pass requires extraction-capable metadata.capability.production_capable=true "
            "whenever non-generated reusable layers are claimed; draft-packaging-only or unrecorded "
            "tooling preflight must remain needs-review"
        )
    tooling_confirmation = confirmation.get("tooling_preflight", {}) if isinstance(confirmation, dict) else {}
    if capability.get("user_choice") != "unset":
        if tooling_confirmation.get("status") != "confirmed":
            errors.append("metadata.confirmation.tooling_preflight must be confirmed before validation")
        elif tooling_confirmation.get("source") not in NON_DEFAULT_CONFIRMATION_SOURCES:
            errors.append(
                "metadata.confirmation.tooling_preflight must come from explicit-user-confirmed or inferred-from-user"
            )
    quality_target = metadata.get("quality_target", {})
    if not isinstance(quality_target, dict):
        errors.append("metadata.quality_target must be an object")
    else:
        if quality_target.get("tier") not in ALLOWED_QUALITY_TARGET_TIERS:
            errors.append(
                "metadata.quality_target.tier must be one of: "
                + ", ".join(sorted(ALLOWED_QUALITY_TARGET_TIERS))
            )
        notes = quality_target.get("notes")
        if not isinstance(notes, str):
            errors.append("metadata.quality_target.notes must be a string")
        if qa_status_for_capability == "pass" and quality_target.get("tier") != "visual-acceptance-ready":
            errors.append("qa.status pass requires metadata.quality_target.tier=visual-acceptance-ready")
    if qa_status_for_capability == "pass":
        for key in ["granularity_alignment", "final_acceptance"]:
            entry = confirmation.get(key, {}) if isinstance(confirmation, dict) else {}
            if entry.get("status") != "confirmed":
                errors.append(f"metadata.confirmation.{key} must be confirmed before qa.status=pass")
            elif entry.get("source") not in NON_DEFAULT_CONFIRMATION_SOURCES:
                errors.append(
                    f"metadata.confirmation.{key} must come from explicit-user-confirmed or inferred-from-user before qa.status=pass"
                )
        if not has_affirmative_decision(decision_log, {"final-acceptance", "final-package-acceptance"}):
            errors.append("qa.status pass requires an affirmative final acceptance decision_log entry")
    qa = metadata.get("qa", {})
    if not isinstance(qa, dict):
        errors.append("metadata.qa must be an object")
        qa = {}
    if "status" not in qa:
        errors.append("metadata.qa missing required field: status")
    elif qa.get("status") not in ALLOWED_QA_STATUSES:
        errors.append("metadata.qa.status must be pass, needs-review, or blocked")


def validate_extraction_pipeline(metadata: dict, errors: list[str]) -> None:
    pipeline = metadata.get("extraction_pipeline", {})
    if not isinstance(pipeline, dict):
        errors.append("metadata.extraction_pipeline must be an object")
        return
    recipe = pipeline.get("recipe")
    if not isinstance(recipe, str) or not recipe.strip():
        errors.append("metadata.extraction_pipeline.recipe must record the chosen pipeline recipe")
    stages = pipeline.get("stages")
    if not isinstance(stages, list) or not stages:
        errors.append("metadata.extraction_pipeline.stages must list the ordered pipeline stages")
    else:
        missing_stages = sorted(REQUIRED_PIPELINE_STAGES - set(stages))
        if missing_stages:
            errors.append(
                "metadata.extraction_pipeline.stages missing required stages: " + ", ".join(missing_stages)
            )
    quality_gates = pipeline.get("quality_gates")
    if not isinstance(quality_gates, list) or not quality_gates or not all(
        isinstance(gate, str) and gate.strip() for gate in quality_gates
    ):
        errors.append("metadata.extraction_pipeline.quality_gates must list non-empty inspected quality gates")
    tools = pipeline.get("tools")
    if not isinstance(tools, list) or not tools:
        errors.append("metadata.extraction_pipeline.tools must list structured tool provenance")
    else:
        for index, tool in enumerate(tools):
            if not isinstance(tool, dict):
                errors.append("metadata.extraction_pipeline.tools entries must include name, role, and version")
                continue
            for field in ["name", "role", "version"]:
                value = tool.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append("metadata.extraction_pipeline.tools entries must include name, role, and version")
