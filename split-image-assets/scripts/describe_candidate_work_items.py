import argparse
import json
from pathlib import Path

from candidate_workflow_lib import (
    candidate_work_item_status_path,
    candidate_delivery_class_for_route,
    list_staged_candidate_records,
    package_relative,
    read_metadata,
    write_json,
)
from package_state_lib import find_plan_object, read_plan_manifest
from provider_bridge_lib import describe_provider_selection


def _recommended_compare_command(
    package_dir: Path,
    object_id: str,
    candidates: list[dict],
    *,
    planned_route: str,
    object_type: str,
    plan_manifest: dict | None,
) -> str:
    package_arg = str(package_dir).replace("\\", "/")
    base_parts = [
        "python",
        "split-image-assets/scripts/compare_candidate_assets.py",
        package_arg,
        "--object-id",
        object_id,
    ]
    provider_ids = sorted(
        {
            str(record.get("provider_id", "")).strip()
            for record in candidates
            if str(record.get("provider_id", "")).strip()
        }
    )
    if planned_route == "generate" and provider_ids:
        parts = [*base_parts]
        if len(provider_ids) == 1:
            parts.extend(["--compare-criterion", "<criterion>"])
            return " ".join(parts)
        if isinstance(plan_manifest, dict):
            selection = describe_provider_selection(plan_manifest, planned_route, object_type, None)
            selected_provider_id = str(selection.get("selected_provider_id", "")).strip()
            selection_source = str(selection.get("selection_source", "")).strip()
            if (
                selection_source == "plan-preference"
                and selected_provider_id
                and selected_provider_id in provider_ids
            ):
                parts.extend(["--provider-id", selected_provider_id])
                parts.extend(["--compare-criterion", "<criterion>"])
                return " ".join(parts)
        parts.extend(["--provider-id", "<provider-id>"])
        parts.extend(["--compare-criterion", "<criterion>"])
        return " ".join(parts)
    parts = [*base_parts]
    for record in candidates:
        parts.extend(["--candidate", f"{record['candidate_id']}={record['relative_asset_path']}"])
    parts.extend(["--compare-criterion", "<criterion>"])
    return " ".join(parts)


def _recommended_promote_command(
    package_dir: Path,
    object_id: str,
    *,
    candidate_id: str,
    candidate_asset_path: str,
    comparison_id: str,
    delivery_class: str,
    selection_reason: str,
) -> str:
    package_arg = str(package_dir).replace("\\", "/")
    parts = [
        "python",
        "split-image-assets/scripts/promote_candidate_asset.py",
        package_arg,
        "--object-id",
        object_id,
        "--delivery-class",
        delivery_class,
        "--repair-note",
        "\"Promote selected candidate.\"",
    ]
    if comparison_id:
        parts.extend(["--comparison-id", comparison_id])
    else:
        parts.extend(["--candidate-id", candidate_id, "--candidate-asset", candidate_asset_path])
    if not comparison_id:
        parts.extend(
            [
                "--selection-reason",
                "\"Explain why this candidate should become the current revision.\"",
            ]
        )
    elif not selection_reason:
        parts.extend(
            [
                "--selection-reason",
                "\"Explain why the selected compare candidate should become the current revision.\"",
            ]
        )
    return " ".join(parts)


def _recommended_promotion_approval_command(
    package_dir: Path,
    object_id: str,
    *,
    comparison_id: str,
    candidate_id: str,
    delivery_class: str,
) -> str:
    package_arg = str(package_dir).replace("\\", "/")
    parts = [
        "python",
        "split-image-assets/scripts/apply_candidate_promotion_decision.py",
        package_arg,
        "--object-id",
        object_id,
    ]
    if comparison_id:
        parts.extend(["--comparison-id", comparison_id])
    parts.extend(
        [
            "--decision-answer",
            "yes",
            "--decision-source",
            "explicit-user-confirmed",
            "--evidence-ref",
            "<approval-evidence-ref>",
        ]
    )
    return " ".join(parts)


def _recommended_selection_command(
    package_dir: Path,
    object_id: str,
    *,
    comparison_id: str,
    candidate_id: str,
    requires_candidate_id: bool,
) -> str:
    package_arg = str(package_dir).replace("\\", "/")
    parts = [
        "python",
        "split-image-assets/scripts/apply_candidate_selection_decision.py",
        package_arg,
        "--object-id",
        object_id,
        "--comparison-id",
        comparison_id,
    ]
    if requires_candidate_id:
        parts.extend(["--candidate-id", "<candidate-id>" if not candidate_id else candidate_id])
    parts.extend(
        [
            "--selection-reason",
            "\"Explain why this candidate wins the compare.\"",
            "--decision-source",
            "explicit-user-confirmed",
            "--evidence-ref",
            "<selection-evidence-ref>",
            "--promotion-answer",
            "skip",
        ]
    )
    return " ".join(parts)


def _command_variant(variant_id: str, label: str, command: str, note: str = "") -> dict:
    return {
        "variant_id": variant_id,
        "label": label,
        "command": command,
        "note": note,
    }


def _selection_command_variants(
    package_dir: Path,
    object_id: str,
    *,
    comparison_id: str,
    candidate_id: str,
    requires_candidate_id: bool,
) -> list[dict]:
    package_arg = str(package_dir).replace("\\", "/")
    base = [
        "python",
        "split-image-assets/scripts/apply_candidate_selection_decision.py",
        package_arg,
        "--object-id",
        object_id,
        "--comparison-id",
        comparison_id,
    ]
    if requires_candidate_id:
        base.extend(["--candidate-id", "<candidate-id>" if not candidate_id else candidate_id])
    base.extend(
        [
            "--selection-reason",
            "\"Explain why this candidate wins the compare.\"",
            "--decision-source",
            "explicit-user-confirmed",
            "--evidence-ref",
            "<selection-evidence-ref>",
        ]
    )
    return [
        _command_variant(
            "selection-only",
            "Record Winner",
            " ".join([*base, "--promotion-answer", "skip"]),
            "Safe default: record compare winner only.",
        ),
        _command_variant(
            "selection-then-promote-yes",
            "Select + Promote",
            " ".join([*base, "--promotion-answer", "yes"]),
            "Records selection first, then continues into promotion approval and promotion.",
        ),
        _command_variant(
            "selection-then-decline",
            "Select + Decline",
            " ".join([*base, "--promotion-answer", "no"]),
            "Records selection first, then records that promotion should not continue.",
        ),
    ]


def _promotion_decision_variants(
    package_dir: Path,
    object_id: str,
    *,
    comparison_id: str,
) -> list[dict]:
    package_arg = str(package_dir).replace("\\", "/")
    base = [
        "python",
        "split-image-assets/scripts/apply_candidate_promotion_decision.py",
        package_arg,
        "--object-id",
        object_id,
    ]
    if comparison_id:
        base.extend(["--comparison-id", comparison_id])
    shared = [
        "--decision-source",
        "explicit-user-confirmed",
        "--evidence-ref",
        "<approval-evidence-ref>",
    ]
    return [
        _command_variant(
            "approve-and-promote",
            "Approve + Promote",
            " ".join([*base, "--decision-answer", "yes", *shared]),
            "Records promotion approval and continues into promotion.",
        ),
        _command_variant(
            "decline-promotion",
            "Decline Promotion",
            " ".join([*base, "--decision-answer", "no", *shared]),
            "Keeps the current revision active and records the decline.",
        ),
    ]


def build_candidate_work_item_status(package_dir: Path, object_id: str | None = None) -> dict:
    metadata = read_metadata(package_dir)
    plan_manifest = read_plan_manifest(package_dir)
    requested_object_id = object_id.strip() if isinstance(object_id, str) and object_id.strip() else ""
    work_items: list[dict] = []

    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        raise ValueError("metadata.json objects must be a list")

    for item in objects:
        if not isinstance(item, dict):
            continue
        current_object_id = str(item.get("id", "")).strip()
        if not current_object_id:
            continue
        if requested_object_id and current_object_id != requested_object_id:
            continue

        plan_object = find_plan_object(plan_manifest, current_object_id)
        planned_route = str(plan_object.get("planned_route", "")).strip() if isinstance(plan_object, dict) else ""
        recommended_delivery_class = candidate_delivery_class_for_route(planned_route)
        candidates = list_staged_candidate_records(package_dir, current_object_id)
        candidate_ids = [record["candidate_id"] for record in candidates]
        candidate_provider_ids = sorted(
            {
                provider_id
                for provider_id in (
                    str(record.get("provider_id", "")).strip() for record in candidates
                )
                if provider_id
            }
        )
        comparisons = item.get("candidate_comparisons", [])
        latest_comparison = comparisons[-1] if isinstance(comparisons, list) and comparisons else {}
        latest_comparison_id = (
            str(latest_comparison.get("comparison_id", "")).strip()
            if isinstance(latest_comparison, dict)
            else ""
        )
        selected_candidate_id = (
            str(item.get("selected_candidate_id", "")).strip()
            if isinstance(item.get("selected_candidate_id", ""), str)
            else ""
        )
        promoted_revision = str(item.get("current_asset_revision", "")).strip()
        confirmation = metadata.get("confirmation", {})
        candidate_promotion_confirmation = (
            confirmation.get("candidate_promotion", {})
            if isinstance(confirmation, dict)
            else {}
        )
        candidate_promotion_status = (
            str(candidate_promotion_confirmation.get("status", "")).strip()
            if isinstance(candidate_promotion_confirmation, dict)
            else ""
        )
        candidate_promotion_source = (
            str(candidate_promotion_confirmation.get("source", "")).strip()
            if isinstance(candidate_promotion_confirmation, dict)
            else ""
        )
        candidate_promotion_evidence_ref = (
            str(candidate_promotion_confirmation.get("evidence_ref", "")).strip()
            if isinstance(candidate_promotion_confirmation, dict)
            else ""
        )
        comparison_selected_candidate_id = (
            str(latest_comparison.get("selected_candidate_id", "")).strip()
            if isinstance(latest_comparison, dict)
            else ""
        )
        comparison_selection_reason = (
            str(latest_comparison.get("selection_reason", "")).strip()
            if isinstance(latest_comparison, dict)
            else ""
        )

        next_action = "no-candidate-work-required"
        next_action_detail = "No candidate-stage action is currently required."
        recommended_command = ""
        recommended_command_variants: list[dict] = []

        if selected_candidate_id and promoted_revision == selected_candidate_id:
            next_action = "no-candidate-work-required"
            next_action_detail = "A candidate has already been promoted as the current revision."
        elif not candidates:
            next_action = "candidate-stage-empty"
            next_action_detail = (
                "No staged repair candidates are present for this object yet."
            )
        elif len(candidates) > 1 and not latest_comparison_id:
            next_action = "compare-candidates"
            next_action_detail = (
                "Multiple staged candidates exist and no comparison evidence has been recorded yet."
            )
            if len(candidate_provider_ids) > 1:
                next_action_detail = (
                    "Multiple staged candidates exist across different provider ids and no comparison evidence has been recorded yet."
                )
                if planned_route == "generate":
                    selection = (
                        describe_provider_selection(
                            plan_manifest,
                            planned_route,
                            str(plan_object.get("object_type", "")).strip(),
                            None,
                        )
                        if isinstance(plan_manifest, dict) and isinstance(plan_object, dict)
                        else {}
                    )
                    selected_provider_id = str(selection.get("selected_provider_id", "")).strip()
                    selection_source = str(selection.get("selection_source", "")).strip()
                    if (
                        selection_source == "plan-preference"
                        and selected_provider_id
                        and selected_provider_id in candidate_provider_ids
                    ):
                        next_action_detail = (
                            "Multiple staged candidates exist across different provider ids; start compare with the plan-selected provider scope so provider-aware auto-discovery stays aligned with the current route plan."
                        )
                    else:
                        next_action_detail = (
                            "Multiple staged candidates exist across different provider ids and no safe provider default is available; choose a provider scope explicitly before compare."
                        )
            recommended_command = _recommended_compare_command(
                package_dir,
                current_object_id,
                candidates,
                planned_route=planned_route,
                object_type=str(plan_object.get("object_type", "")).strip() if isinstance(plan_object, dict) else "",
                plan_manifest=plan_manifest if isinstance(plan_manifest, dict) else None,
            )
        elif latest_comparison_id and not comparison_selected_candidate_id:
            next_action = "await-candidate-selection"
            next_action_detail = (
                "Comparison evidence exists, but no selected candidate has been recorded for the latest comparison."
            )
            compare_candidate_ids = latest_comparison.get("candidate_ids", []) if isinstance(latest_comparison, dict) else []
            single_candidate_id = (
                compare_candidate_ids[0]
                if isinstance(compare_candidate_ids, list)
                and len(compare_candidate_ids) == 1
                and isinstance(compare_candidate_ids[0], str)
                and compare_candidate_ids[0].strip()
                else ""
            )
            recommended_command = _recommended_selection_command(
                package_dir,
                current_object_id,
                comparison_id=latest_comparison_id,
                candidate_id=single_candidate_id,
                requires_candidate_id=not bool(single_candidate_id),
            )
            recommended_command_variants = _selection_command_variants(
                package_dir,
                current_object_id,
                comparison_id=latest_comparison_id,
                candidate_id=single_candidate_id,
                requires_candidate_id=not bool(single_candidate_id),
            )
        else:
            candidate_id = comparison_selected_candidate_id or (candidate_ids[0] if len(candidate_ids) == 1 else "")
            candidate_asset_path = ""
            if latest_comparison_id and isinstance(latest_comparison, dict):
                compare_candidate_ids = latest_comparison.get("candidate_ids", [])
                if isinstance(compare_candidate_ids, list) and candidate_id and candidate_id in compare_candidate_ids:
                    compare_manifest_path = str(latest_comparison.get("compare_manifest_path", "")).strip()
                    if compare_manifest_path:
                        compare_manifest = json.loads(
                            (package_dir / compare_manifest_path).read_text(encoding="utf-8")
                        )
                        for entry in compare_manifest.get("candidates", []):
                            if isinstance(entry, dict) and entry.get("candidate_id") == candidate_id:
                                candidate_asset_path = str(entry.get("asset_path", "")).strip()
                                break
            if not candidate_asset_path and candidate_id:
                candidate_asset_path = next(
                    (
                        str(record.get("relative_asset_path", "")).strip()
                        for record in candidates
                        if record.get("candidate_id") == candidate_id
                    ),
                    "",
                )

            if latest_comparison_id and candidate_id:
                if candidate_promotion_status in {"confirmed", "not-required"}:
                    next_action = "promote-selected-candidate"
                    next_action_detail = (
                        "Comparison evidence is present and candidate promotion approval has already been recorded."
                    )
                    recommended_command = _recommended_promote_command(
                        package_dir,
                        current_object_id,
                        candidate_id=candidate_id,
                        candidate_asset_path=candidate_asset_path,
                        comparison_id=latest_comparison_id,
                        delivery_class=recommended_delivery_class,
                        selection_reason=comparison_selection_reason,
                    )
                else:
                    next_action = "record-candidate-promotion-approval"
                    next_action_detail = (
                        "A compare-selected candidate exists, but the candidate_promotion approval gate is still pending."
                    )
                    recommended_command = _recommended_promotion_approval_command(
                        package_dir,
                        current_object_id,
                        comparison_id=latest_comparison_id,
                        candidate_id=candidate_id,
                        delivery_class=recommended_delivery_class,
                    )
                    recommended_command_variants = _promotion_decision_variants(
                        package_dir,
                        current_object_id,
                        comparison_id=latest_comparison_id,
                    )
            elif len(candidates) == 1:
                if candidate_promotion_status in {"confirmed", "not-required"}:
                    next_action = "promote-single-candidate"
                    next_action_detail = (
                        "Exactly one staged candidate exists and promotion approval has already been recorded."
                    )
                    recommended_command = _recommended_promote_command(
                        package_dir,
                        current_object_id,
                        candidate_id=candidate_ids[0],
                        candidate_asset_path=str(candidates[0].get("relative_asset_path", "")).strip(),
                        comparison_id="",
                        delivery_class=recommended_delivery_class,
                        selection_reason="",
                    )
                else:
                    next_action = "record-candidate-promotion-approval"
                    next_action_detail = (
                        "Exactly one staged candidate exists, but candidate_promotion approval is still pending."
                    )
                    recommended_command = _recommended_promotion_approval_command(
                        package_dir,
                        current_object_id,
                        comparison_id="",
                        candidate_id=candidate_ids[0],
                        delivery_class=recommended_delivery_class,
                    )
                    recommended_command_variants = _promotion_decision_variants(
                        package_dir,
                        current_object_id,
                        comparison_id="",
                    )

        work_items.append(
            {
                "object_id": current_object_id,
                "planned_route": planned_route,
                "staged_candidate_count": len(candidates),
                "candidate_ids": candidate_ids,
                "candidate_provider_ids": candidate_provider_ids,
                "candidate_provider_stage_manifest_paths": [
                    str(record.get("provider_stage_manifest_path", "")).strip()
                    for record in candidates
                    if str(record.get("provider_stage_manifest_path", "")).strip()
                ],
                "latest_comparison_id": latest_comparison_id,
                "comparison_selected_candidate_id": comparison_selected_candidate_id,
                "comparison_selection_reason": comparison_selection_reason,
                "candidate_promotion_status": candidate_promotion_status,
                "candidate_promotion_source": candidate_promotion_source,
                "candidate_promotion_evidence_ref": candidate_promotion_evidence_ref,
                "selected_candidate_id": selected_candidate_id,
                "current_asset_revision": promoted_revision,
                "recommended_delivery_class": recommended_delivery_class,
                "next_action": next_action,
                "next_action_detail": next_action_detail,
                "recommended_command": recommended_command,
                "recommended_command_variants": recommended_command_variants,
            }
        )

    if requested_object_id and not work_items:
        raise ValueError(f"metadata.json is missing object id: {requested_object_id}")

    return {
        "schema_version": "1.0",
        "package_name": str(metadata.get("package_name", "")).strip(),
        "objects": work_items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write candidate work-item status for staged repair candidates and comparison evidence."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", help="Optional object id filter.", default="")
    args = parser.parse_args()

    try:
        package_dir = Path(args.package_dir).resolve()
        status = build_candidate_work_item_status(package_dir, args.object_id)
        path = candidate_work_item_status_path(package_dir)
        write_json(path, status)
    except ValueError as exc:
        parser.error(str(exc))

    payload = {
        "candidate_work_items_path": package_relative(package_dir, path),
        "object_count": len(status["objects"]),
        "objects": status["objects"],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
