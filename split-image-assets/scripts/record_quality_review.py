import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_QA_STATUSES = {"pass", "needs-review", "blocked"}
ALLOWED_QUALITY_CHECK_STATUSES = {"pass", "needs-review", "blocked", "unknown"}
QUALITY_CHECK_ARGS = {
    "mask_alignment": "mask_alignment",
    "alpha_edges": "alpha_edges",
    "background_residue": "background_residue",
    "reuse_readiness": "reuse_readiness",
}
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
STAGE_TO_CONFIRMATION_KEY = {
    "tooling-preflight": "tooling_preflight",
    "granularity-alignment": "granularity_alignment",
    "pilot-object-gate": "pilot_object",
    "approximate-reconstruction-acceptance": "approximate_reconstruction",
    "approximate-reconstruction-acceptance-gate": "approximate_reconstruction",
    "reconstruction-acceptance": "approximate_reconstruction",
    "final-acceptance": "final_acceptance",
    "final-promotion-acceptance": "candidate_promotion",
}
DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION = {
    "tooling_preflight": "external-blocker",
    "granularity_alignment": "user-decision",
    "pilot_object": "formal-approval",
    "approximate_reconstruction": "formal-approval",
    "final_acceptance": "formal-approval",
    "candidate_promotion": "formal-approval",
}


def read_metadata(package_dir: Path, parser: argparse.ArgumentParser) -> dict:
    metadata_path = package_dir / "metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error(f"metadata.json is missing: {metadata_path}")
    except json.JSONDecodeError as exc:
        parser.error(f"metadata.json is not valid JSON: {exc}")
    if not isinstance(metadata, dict):
        parser.error("metadata.json must contain an object")
    return metadata


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def object_map(metadata: dict, parser: argparse.ArgumentParser) -> dict[str, dict]:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        parser.error("metadata.objects must be a list before review can be recorded")
    mapped: dict[str, dict] = {}
    for item in objects:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            mapped[item["id"]] = item
    return mapped


def selected_objects(metadata: dict, args: argparse.Namespace, parser: argparse.ArgumentParser) -> list[dict]:
    mapped = object_map(metadata, parser)
    if args.all_objects:
        return list(mapped.values())
    if not args.object_id:
        return []
    missing = [object_id for object_id in args.object_id if object_id not in mapped]
    if missing:
        parser.error("unknown object-id for review: " + ", ".join(missing))
    return [mapped[object_id] for object_id in args.object_id]


def has_quality_updates(args: argparse.Namespace) -> bool:
    return any(getattr(args, name) is not None for name in QUALITY_CHECK_ARGS)


def has_classification_updates(args: argparse.Namespace) -> bool:
    return args.asset_class is not None or args.reuse_status is not None


def has_object_targeted_updates(args: argparse.Namespace) -> bool:
    return any(
        value is not None
        for value in [
            args.object_type,
            args.asset_class,
            args.reuse_status,
            args.delivery_class,
            args.current_asset_revision,
            args.active_reconstruction_method,
            args.selected_candidate_id,
            args.text_role,
            args.text_render_class,
            args.editability_score,
            args.visual_complexity_score,
            args.asset_value_score,
            args.scoring_reason,
            args.recommended_action,
            args.final_action,
            args.routing_decision_source,
            args.rebuildable_downstream,
            args.rebuild_notes,
        ]
    ) or bool(args.repair_history_entry)


def has_routing_action_updates(args: argparse.Namespace) -> bool:
    return args.recommended_action is not None or args.final_action is not None


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


def require_pause_category(value: str | None, flag_name: str) -> str:
    if not value:
        raise ValueError(f"{flag_name} is required for formal gate writes")
    if value not in ALLOWED_PAUSE_CATEGORIES:
        raise ValueError(
            f"{flag_name} must be one of: " + ", ".join(sorted(ALLOWED_PAUSE_CATEGORIES))
        )
    return value


def require_formal_source(source: str | None, flag_name: str, evidence_ref: str | None) -> str:
    if not source:
        raise ValueError(f"{flag_name} is required for formal gate writes")
    if source not in ALLOWED_DECISION_SOURCES:
        raise ValueError(
            f"{flag_name} must be one of: " + ", ".join(sorted(ALLOWED_DECISION_SOURCES))
        )
    if source == "inferred-from-user" and (evidence_ref is None or not evidence_ref.strip()):
        raise ValueError("--evidence-ref is required when source is inferred-from-user")
    return source


def normalized_blocking(value: str | None) -> str:
    if not value:
        raise ValueError("--blocking is required for formal decision-log writes")
    if value not in ALLOWED_BLOCKING_VALUES:
        raise ValueError("--blocking must be one of: false, true")
    return value


def update_analysis(metadata: dict, args: argparse.Namespace) -> None:
    analysis = metadata.setdefault("analysis", {})
    if args.visual_hierarchy:
        analysis["visual_hierarchy"] = args.visual_hierarchy
    if args.recommended_split_plan:
        analysis["recommended_split_plan"] = args.recommended_split_plan


def update_quality_gates(metadata: dict, gates: list[str] | None) -> None:
    if not gates:
        return
    pipeline = metadata.setdefault("extraction_pipeline", {})
    quality_gates = pipeline.setdefault("quality_gates", [])
    for gate in gates:
        if gate not in quality_gates:
            quality_gates.append(gate)


def update_granularity(metadata: dict, args: argparse.Namespace) -> None:
    if (
        not args.granularity_mode
        and not args.granularity_confirmed
        and not args.granularity_note
        and args.scope_strategy is None
        and args.text_handling is None
        and args.carrier_glyph_policy is None
        and args.background_expectation is None
        and args.layer_independence is None
    ):
        return
    granularity = metadata.setdefault("granularity", {})
    if args.granularity_mode:
        granularity["mode"] = args.granularity_mode
    if args.granularity_confirmed:
        granularity["user_confirmed"] = True
    if args.granularity_note:
        existing = granularity.get("notes", "")
        if existing:
            granularity["notes"] = existing.rstrip() + "\n" + args.granularity_note
        else:
            granularity["notes"] = args.granularity_note
    if args.scope_strategy is not None:
        granularity["scope_strategy"] = args.scope_strategy
    if args.text_handling is not None:
        granularity["text_handling"] = args.text_handling
    if args.carrier_glyph_policy is not None:
        granularity["carrier_glyph_policy"] = args.carrier_glyph_policy
    if args.background_expectation is not None:
        granularity["background_expectation"] = args.background_expectation
    if args.layer_independence is not None:
        granularity["layer_independence"] = args.layer_independence


def update_decision_log(metadata: dict, args: argparse.Namespace) -> None:
    decision_values = [
        args.decision_stage,
        args.decision_question,
        args.decision_recommended,
        args.decision_answer,
        args.decision_effect,
    ]
    if not any(decision_values):
        return
    if not all(decision_values):
        missing = [
            name
            for name, value in [
                ("--decision-stage", args.decision_stage),
                ("--decision-question", args.decision_question),
                ("--decision-recommended", args.decision_recommended),
                ("--decision-answer", args.decision_answer),
                ("--decision-effect", args.decision_effect),
            ]
            if not value
        ]
        raise ValueError("decision log updates require: " + ", ".join(missing))
    pause_category = require_pause_category(args.pause_category, "--pause-category")
    decision_source = require_formal_source(
        args.decision_source, "--decision-source", args.evidence_ref
    )
    blocking = normalized_blocking(args.blocking)
    decision_log = metadata.setdefault("decision_log", [])
    if not isinstance(decision_log, list):
        raise ValueError("metadata.decision_log must be a list before recording decisions")
    entry = {
        "stage": args.decision_stage,
        "pause_category": pause_category,
        "question": args.decision_question,
        "recommended_answer": args.decision_recommended,
        "recorded_answer": args.decision_answer,
        "decision_effect": args.decision_effect,
        "decision_source": decision_source,
        "evidence_ref": args.evidence_ref or "",
        "blocking": blocking,
    }
    if args.object_id and len(args.object_id) == 1:
        entry["object_id"] = args.object_id[0]
    decision_log.append(entry)


def update_confirmation(metadata: dict, args: argparse.Namespace) -> None:
    confirmation = metadata.setdefault("confirmation", {})
    if args.confirmation_key is not None:
        if args.confirmation_status is None:
            raise ValueError("--confirmation-status is required when --confirmation-key is provided")
        source = args.confirmation_source
        if source is None and args.confirmation_status == "pending":
            source = "unset"
        if args.confirmation_status in {"confirmed", "not-required"} and source == "unset":
            raise ValueError(
                "--confirmation-source must be explicit-user-confirmed or inferred-from-user "
                f"when --confirmation-status is {args.confirmation_status}"
            )
        if args.confirmation_status == "pending" and source not in {None, "unset"}:
            raise ValueError("--confirmation-source must be unset when --confirmation-status is pending")
        if source != "unset":
            require_formal_source(source, "--confirmation-source", args.evidence_ref)
            pause_category = require_pause_category(args.pause_category, "--pause-category")
        else:
            pause_category = args.pause_category or DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION.get(
                args.confirmation_key, ""
            )
        entry = confirmation.setdefault(args.confirmation_key, default_confirmation_entry(args.confirmation_key))
        entry["status"] = args.confirmation_status
        entry["source"] = source
        entry["pause_category"] = pause_category
        if args.confirmation_note is not None:
            entry["notes"] = args.confirmation_note
        entry["evidence_ref"] = args.evidence_ref or ""
        if args.confirmation_object_id is not None:
            entry["object_id"] = args.confirmation_object_id

    if args.decision_stage:
        key = STAGE_TO_CONFIRMATION_KEY.get(args.decision_stage)
        if key:
            entry = confirmation.setdefault(
                key,
                default_confirmation_entry(key),
            )
            entry["status"] = "confirmed"
            entry["source"] = require_formal_source(
                args.decision_source, "--decision-source", args.evidence_ref
            )
            entry["pause_category"] = require_pause_category(
                args.pause_category, "--pause-category"
            )
            if args.confirmation_note is not None:
                entry["notes"] = args.confirmation_note
            elif not entry.get("notes"):
                entry["notes"] = args.decision_effect
            entry["evidence_ref"] = args.evidence_ref or ""
            if key == "pilot_object" and args.confirmation_object_id is not None:
                entry["object_id"] = args.confirmation_object_id


def parse_bool(value: str, flag_name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"{flag_name} must be true or false")


def update_capability(metadata: dict, args: argparse.Namespace) -> None:
    if (
        args.production_capable is None
        and not args.missing_for_production
        and args.capability_user_choice is None
        and args.capability_note is None
    ):
        return
    capability = metadata.setdefault("capability", {})
    if args.production_capable is not None:
        capability["production_capable"] = parse_bool(args.production_capable, "--production-capable")
    if args.missing_for_production is not None:
        capability["missing_for_production"] = args.missing_for_production
    elif "missing_for_production" not in capability:
        capability["missing_for_production"] = []
    if args.capability_user_choice is not None:
        if args.capability_user_choice not in ALLOWED_CAPABILITY_CHOICES:
            raise ValueError(
                "--capability-user-choice must be one of: "
                + ", ".join(sorted(ALLOWED_CAPABILITY_CHOICES))
            )
        capability["user_choice"] = args.capability_user_choice
    if args.capability_note is not None:
        capability["notes"] = args.capability_note


def update_quality_target(metadata: dict, args: argparse.Namespace) -> None:
    if args.quality_target_tier is None and args.quality_target_note is None:
        return
    quality_target = metadata.setdefault("quality_target", {})
    if args.quality_target_tier is not None:
        quality_target["tier"] = args.quality_target_tier
    if args.quality_target_note is not None:
        quality_target["notes"] = args.quality_target_note


def update_object_checks(objects: list[dict], args: argparse.Namespace) -> None:
    for item in objects:
        if args.object_type is not None:
            item["object_type"] = args.object_type
        if args.asset_class is not None:
            item["asset_class"] = args.asset_class
        if args.reuse_status is not None:
            item["reuse_status"] = args.reuse_status
        if args.delivery_class is not None:
            item["delivery_class"] = args.delivery_class
        if args.current_asset_revision is not None:
            item["current_asset_revision"] = args.current_asset_revision
        if args.active_reconstruction_method is not None:
            item["active_reconstruction_method"] = args.active_reconstruction_method
        if args.selected_candidate_id is not None:
            item["selected_candidate_id"] = args.selected_candidate_id
        if args.repair_history_entry:
            repair_history = item.setdefault("repair_history", [])
            for entry in args.repair_history_entry:
                repair_history.append(entry)
        text_semantics = item.setdefault(
            "text_semantics",
            {
                "text_role": "non-text",
                "text_render_class": "non-text",
            },
        )
        if args.text_role is not None:
            text_semantics["text_role"] = args.text_role
        if args.text_render_class is not None:
            text_semantics["text_render_class"] = args.text_render_class
        value_scoring = item.setdefault(
            "value_scoring",
            {
                "editability_score": "unset",
                "visual_complexity_score": "unset",
                "asset_value_score": "unset",
                "scoring_reason": "",
            },
        )
        if args.editability_score is not None:
            value_scoring["editability_score"] = args.editability_score
        if args.visual_complexity_score is not None:
            value_scoring["visual_complexity_score"] = args.visual_complexity_score
        if args.asset_value_score is not None:
            value_scoring["asset_value_score"] = args.asset_value_score
        if args.scoring_reason is not None:
            value_scoring["scoring_reason"] = args.scoring_reason
        decision_routing = item.setdefault(
            "decision_routing",
            {
                "recommended_action": "unset",
                "final_action": "unset",
                "decision_source": "unset",
            },
        )
        if args.recommended_action is not None:
            decision_routing["recommended_action"] = args.recommended_action
        if args.final_action is not None:
            decision_routing["final_action"] = args.final_action
        if args.routing_decision_source is not None:
            decision_routing["decision_source"] = args.routing_decision_source
        rebuild_intent = item.setdefault(
            "rebuild_intent",
            {
                "rebuildable_downstream": False,
                "rebuild_notes": "",
            },
        )
        if args.rebuildable_downstream is not None:
            rebuild_intent["rebuildable_downstream"] = parse_bool(
                args.rebuildable_downstream, "--rebuildable-downstream"
            )
        if args.rebuild_notes is not None:
            rebuild_intent["rebuild_notes"] = args.rebuild_notes
        quality_checks = item.setdefault("quality_checks", {})
        for arg_name, check_name in QUALITY_CHECK_ARGS.items():
            value = getattr(args, arg_name)
            if value is not None:
                quality_checks[check_name] = value
        if args.confirm_crop_layer:
            item["manual_review_confirmed"] = True
            notes = item.setdefault("manual_review_notes", [])
            for note in args.review_note or ["Manual review confirmed crop-only layer."]:
                if note not in notes:
                    notes.append(note)


def all_required_checks_pass(metadata: dict) -> bool:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list) or not objects:
        return False
    required = set(QUALITY_CHECK_ARGS.values())
    for item in objects:
        if not isinstance(item, dict):
            return False
        quality_checks = item.get("quality_checks")
        if not isinstance(quality_checks, dict):
            return False
        if required - set(quality_checks):
            return False
        for check_name in required:
            if quality_checks.get(check_name) != "pass":
                return False
    return True


def reusable_layers_ready_for_pass(metadata: dict) -> bool:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list) or not objects:
        return False
    for item in objects:
        if not isinstance(item, dict):
            return False
        asset_class = item.get("asset_class")
        reuse_status = item.get("reuse_status")
        if asset_class in {"atomic", "candidate"} and reuse_status != "production-ready":
            return False
    return True


def capability_allows_pass(metadata: dict) -> bool:
    capability = metadata.get("capability")
    return isinstance(capability, dict) and capability.get("production_capable") is True


def has_affirmative_decision(metadata: dict, stages: set[str]) -> bool:
    decision_log = metadata.get("decision_log", [])
    if not isinstance(decision_log, list):
        return False
    return any(
        isinstance(entry, dict)
        and entry.get("stage") in stages
        and is_affirmative_answer(entry.get("user_answer"))
        for entry in decision_log
    )


def update_asset_summary(metadata: dict) -> None:
    summary = {
        "production_ready_assets": 0,
        "draft_candidate_assets": 0,
        "support_only_layers": 0,
        "blocked_assets": 0,
    }
    objects = metadata.get("objects", [])
    if isinstance(objects, list):
        for item in objects:
            if not isinstance(item, dict):
                continue
            asset_class = item.get("asset_class")
            reuse_status = item.get("reuse_status")
            if asset_class == "atomic" and reuse_status == "production-ready":
                summary["production_ready_assets"] += 1
            elif reuse_status == "draft-candidate":
                summary["draft_candidate_assets"] += 1
            elif reuse_status in {"support-only", "approximate-reconstruction"} or asset_class in {
                "grouped-support",
                "background-support",
                "preview-reference",
            }:
                summary["support_only_layers"] += 1
            elif reuse_status == "blocked":
                summary["blocked_assets"] += 1
    metadata["asset_summary"] = summary


def append_qa_report(package_dir: Path, args: argparse.Namespace) -> None:
    qa_path = package_dir / "qa_report.md"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["", "## Quality Review Update", "", f"- Time: {timestamp}"]
    if args.qa_status:
        lines.append(f"- QA status: {args.qa_status}")
    if args.granularity_mode:
        lines.append(f"- Granularity mode: {args.granularity_mode}")
    if args.granularity_confirmed:
        lines.append("- Granularity confirmed: true")
    if args.granularity_note:
        lines.append(f"- Granularity note: {args.granularity_note}")
    if args.scope_strategy:
        lines.append(f"- Scope strategy: {args.scope_strategy}")
    if args.text_handling:
        lines.append(f"- Text handling: {args.text_handling}")
    if args.carrier_glyph_policy:
        lines.append(f"- Carrier/glyph policy: {args.carrier_glyph_policy}")
    if args.background_expectation:
        lines.append(f"- Background expectation: {args.background_expectation}")
    if args.layer_independence:
        lines.append(f"- Layer independence: {args.layer_independence}")
    if args.decision_stage:
        lines.append(f"- Decision stage: {args.decision_stage}")
        lines.append(f"- Pause category: {args.pause_category}")
        lines.append(f"- Decision question: {args.decision_question}")
        lines.append(f"- Recommended answer: {args.decision_recommended}")
        lines.append(f"- Recorded answer: {args.decision_answer}")
        lines.append(f"- Decision effect: {args.decision_effect}")
        lines.append(f"- Decision source: {args.decision_source}")
        lines.append(f"- Evidence ref: {args.evidence_ref or ''}")
        lines.append(f"- Blocking: {args.blocking}")
    if args.production_capable is not None:
        lines.append(f"- Production capable: {args.production_capable}")
    if args.missing_for_production:
        lines.append("- Missing for production: " + ", ".join(args.missing_for_production))
    if args.capability_user_choice:
        lines.append(f"- Capability user choice: {args.capability_user_choice}")
    if args.capability_note:
        lines.append(f"- Capability note: {args.capability_note}")
    if args.quality_target_tier:
        lines.append(f"- Quality target tier: {args.quality_target_tier}")
    if args.quality_target_note:
        lines.append(f"- Quality target note: {args.quality_target_note}")
    if args.object_id:
        lines.append("- Objects: " + ", ".join(args.object_id))
    elif args.all_objects:
        lines.append("- Objects: all")
    if args.object_type:
        lines.append(f"- Object type: {args.object_type}")
    if args.text_role:
        lines.append(f"- Text role: {args.text_role}")
    if args.text_render_class:
        lines.append(f"- Text render class: {args.text_render_class}")
    if args.editability_score:
        lines.append(f"- Editability score: {args.editability_score}")
    if args.visual_complexity_score:
        lines.append(f"- Visual complexity score: {args.visual_complexity_score}")
    if args.asset_value_score:
        lines.append(f"- Asset value score: {args.asset_value_score}")
    if args.recommended_action:
        lines.append(f"- Recommended action: {args.recommended_action}")
    if args.final_action:
        lines.append(f"- Final action: {args.final_action}")
    if args.routing_decision_source:
        lines.append(f"- Routing decision source: {args.routing_decision_source}")
    if args.rebuildable_downstream:
        lines.append(f"- Rebuildable downstream: {args.rebuildable_downstream}")
    if args.confirmation_key:
        lines.append(f"- Confirmation gate: {args.confirmation_key}")
        lines.append(f"- Confirmation status: {args.confirmation_status}")
        lines.append(f"- Confirmation source: {args.confirmation_source or 'unset'}")
        lines.append(
            f"- Confirmation pause category: {args.pause_category or DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION.get(args.confirmation_key, '')}"
        )
        lines.append(f"- Confirmation evidence ref: {args.evidence_ref or ''}")
    if args.confirmation_object_id:
        lines.append(f"- Pilot object: {args.confirmation_object_id}")
    if args.asset_class:
        lines.append(f"- Asset class: {args.asset_class}")
    if args.reuse_status:
        lines.append(f"- Reuse status: {args.reuse_status}")
    for note in args.review_note or []:
        lines.append(f"- Note: {note}")
    existing = qa_path.read_text(encoding="utf-8") if qa_path.exists() else ""
    qa_path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record semantic analysis and manual QA decisions for a split asset package."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--visual-hierarchy", action="append", help="Semantic layer, repeatable.")
    parser.add_argument("--recommended-split-plan", help="Semantic split plan summary.")
    parser.add_argument("--granularity-mode", choices=sorted(ALLOWED_GRANULARITY_MODES))
    parser.add_argument("--granularity-confirmed", action="store_true")
    parser.add_argument("--granularity-note")
    parser.add_argument("--scope-strategy", choices=sorted(ALLOWED_SCOPE_STRATEGIES))
    parser.add_argument("--text-handling", choices=sorted(ALLOWED_TEXT_HANDLING))
    parser.add_argument("--carrier-glyph-policy", choices=sorted(ALLOWED_CARRIER_GLYPH_POLICIES))
    parser.add_argument("--background-expectation", choices=sorted(ALLOWED_BACKGROUND_EXPECTATIONS))
    parser.add_argument("--layer-independence", choices=sorted(ALLOWED_LAYER_INDEPENDENCE))
    parser.add_argument("--decision-stage")
    parser.add_argument("--decision-question")
    parser.add_argument("--decision-recommended")
    parser.add_argument("--decision-answer")
    parser.add_argument("--decision-effect")
    parser.add_argument("--decision-source", choices=sorted(ALLOWED_DECISION_SOURCES))
    parser.add_argument("--pause-category", choices=sorted(ALLOWED_PAUSE_CATEGORIES))
    parser.add_argument("--blocking", choices=sorted(ALLOWED_BLOCKING_VALUES))
    parser.add_argument("--evidence-ref")
    parser.add_argument("--production-capable", choices=["true", "false"])
    parser.add_argument("--missing-for-production", action="append")
    parser.add_argument("--capability-user-choice")
    parser.add_argument("--capability-note")
    parser.add_argument("--quality-target-tier", choices=sorted(ALLOWED_QUALITY_TARGET_TIERS))
    parser.add_argument("--quality-target-note")
    parser.add_argument(
        "--confirmation-key",
        choices=sorted(
            {
                "tooling_preflight",
                "granularity_alignment",
                "pilot_object",
                "approximate_reconstruction",
                "final_promotion_acceptance",
                "final_acceptance",
                "candidate_promotion",
            }
        ),
    )
    parser.add_argument("--confirmation-status", choices=sorted(ALLOWED_CONFIRMATION_STATUSES))
    parser.add_argument("--confirmation-source", choices=sorted(ALLOWED_CONFIRMATION_SOURCES))
    parser.add_argument("--confirmation-note")
    parser.add_argument("--confirmation-object-id")
    parser.add_argument("--quality-gate", action="append", help="Pipeline quality gate inspected.")
    parser.add_argument("--object-id", action="append", help="Object id whose quality checks are updated.")
    parser.add_argument("--all-objects", action="store_true", help="Apply quality check updates to all objects.")
    parser.add_argument("--object-type", choices=sorted(ALLOWED_OBJECT_TYPES))
    parser.add_argument("--text-role", choices=sorted(ALLOWED_TEXT_ROLES))
    parser.add_argument("--text-render-class", choices=sorted(ALLOWED_TEXT_RENDER_CLASSES))
    parser.add_argument("--editability-score", choices=sorted(ALLOWED_SCORE_VALUES))
    parser.add_argument("--visual-complexity-score", choices=sorted(ALLOWED_SCORE_VALUES))
    parser.add_argument("--asset-value-score", choices=sorted(ALLOWED_SCORE_VALUES))
    parser.add_argument("--scoring-reason")
    parser.add_argument("--recommended-action", choices=sorted(ALLOWED_ROUTING_ACTIONS))
    parser.add_argument("--final-action", choices=sorted(ALLOWED_ROUTING_ACTIONS))
    parser.add_argument(
        "--routing-decision-source",
        choices=sorted(ALLOWED_ROUTING_DECISION_SOURCES),
    )
    parser.add_argument("--rebuildable-downstream", choices=["true", "false"])
    parser.add_argument("--rebuild-notes")
    parser.add_argument("--asset-class", choices=sorted(ALLOWED_ASSET_CLASSES))
    parser.add_argument("--reuse-status", choices=sorted(ALLOWED_REUSE_STATUSES))
    parser.add_argument("--delivery-class", choices=sorted(ALLOWED_DELIVERY_CLASSES))
    parser.add_argument("--current-asset-revision")
    parser.add_argument("--active-reconstruction-method")
    parser.add_argument("--selected-candidate-id")
    parser.add_argument(
        "--repair-history-entry",
        action="append",
        help="Append a repair or candidate selection note for the targeted object.",
    )
    parser.add_argument("--mask-alignment", choices=sorted(ALLOWED_QUALITY_CHECK_STATUSES))
    parser.add_argument("--alpha-edges", choices=sorted(ALLOWED_QUALITY_CHECK_STATUSES))
    parser.add_argument("--background-residue", choices=sorted(ALLOWED_QUALITY_CHECK_STATUSES))
    parser.add_argument("--reuse-readiness", choices=sorted(ALLOWED_QUALITY_CHECK_STATUSES))
    parser.add_argument("--qa-status", choices=sorted(ALLOWED_QA_STATUSES))
    parser.add_argument(
        "--confirm-crop-layer",
        action="store_true",
        help="Record human confirmation that an estimated crop/bbox layer is acceptable.",
    )
    parser.add_argument("--review-note", action="append")
    args = parser.parse_args()

    if args.all_objects and args.object_id:
        parser.error("use either --all-objects or --object-id, not both")
    if has_quality_updates(args) and not args.all_objects and not args.object_id:
        parser.error("quality check updates require --object-id or --all-objects")
    if has_object_targeted_updates(args) and not args.all_objects and not args.object_id:
        parser.error("object-targeted updates require --object-id or --all-objects")
    if args.confirm_crop_layer and not args.all_objects and not args.object_id:
        parser.error("--confirm-crop-layer requires --object-id or --all-objects")
    if has_routing_action_updates(args) and args.routing_decision_source in {None, "unset"}:
        parser.error("--routing-decision-source is required when routing actions are updated")
    if (
        has_routing_action_updates(args)
        and args.routing_decision_source == "inferred-from-user"
        and (args.evidence_ref is None or not args.evidence_ref.strip())
    ):
        parser.error(
            "--evidence-ref is required when --routing-decision-source is inferred-from-user"
        )

    package_dir = Path(args.package_dir).resolve()
    metadata = read_metadata(package_dir, parser)
    targets = selected_objects(metadata, args, parser)

    update_analysis(metadata, args)
    update_granularity(metadata, args)
    try:
        update_decision_log(metadata, args)
        update_capability(metadata, args)
        update_quality_target(metadata, args)
        update_confirmation(metadata, args)
    except ValueError as exc:
        parser.error(str(exc))
    update_quality_gates(metadata, args.quality_gate)
    update_object_checks(targets, args)
    update_asset_summary(metadata)

    if args.qa_status == "pass" and not all_required_checks_pass(metadata):
        parser.error("cannot set qa-status pass until every required object quality check is pass")
    if args.qa_status == "pass" and not capability_allows_pass(metadata):
        parser.error("cannot set qa-status pass until metadata.capability.production_capable is true")
    quality_target = metadata.get("quality_target", {})
    if args.qa_status == "pass" and (
        not isinstance(quality_target, dict)
        or quality_target.get("tier") != "visual-acceptance-ready"
    ):
        parser.error(
            "cannot set qa-status pass until metadata.quality_target.tier is visual-acceptance-ready"
        )
    if args.qa_status == "pass" and not reusable_layers_ready_for_pass(metadata):
        parser.error("cannot set qa-status pass until reusable layers are reuse_status=production-ready")
    if args.qa_status == "pass":
        decision_log = metadata.get("decision_log", [])
        if not isinstance(decision_log, list) or not decision_log:
            parser.error(
                "cannot set qa-status pass until at least one decision_log entry records user acceptance"
            )
        if not has_affirmative_decision(metadata, {"final-acceptance", "final-package-acceptance"}):
            parser.error(
                "cannot set qa-status pass until a final acceptance decision records an affirmative user answer"
            )
        final_acceptance = metadata.get("confirmation", {}).get("final_acceptance", {})
        if not isinstance(final_acceptance, dict) or final_acceptance.get("status") != "confirmed":
            parser.error(
                "cannot set qa-status pass until metadata.confirmation.final_acceptance is confirmed"
            )
    if args.qa_status:
        metadata.setdefault("qa", {})["status"] = args.qa_status

    write_metadata(package_dir, metadata)
    append_qa_report(package_dir, args)
    print(f"Recorded quality review: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
