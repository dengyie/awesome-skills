import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from candidate_workflow_lib import load_provider_stage_manifest
from package_state_lib import update_asset_summary


def read_metadata(package_dir: Path) -> dict:
    return json.loads((package_dir / "metadata.json").read_text(encoding="utf-8"))


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def package_path(package_dir: Path, value: object, label: str, parser: argparse.ArgumentParser) -> Path:
    if not isinstance(value, str) or not value.strip():
        parser.error(f"{label} must be a package-relative path")
    raw_path = Path(value)
    if raw_path.is_absolute():
        parser.error(f"{label} must stay inside the package: {value}")
    resolved = (package_dir / raw_path).resolve()
    package_root = package_dir.resolve()
    if resolved != package_root and package_root not in resolved.parents:
        parser.error(f"{label} must stay inside the package: {value}")
    return resolved


def require_repair_candidate_path(path: Path, package_dir: Path, label: str, parser: argparse.ArgumentParser) -> None:
    expected_root = (package_dir / "_staging" / "repair_candidates").resolve()
    if path != expected_root and expected_root not in path.parents:
        parser.error(f"{label} must be staged under _staging/repair_candidates/: {path}")


def append_qa_report(package_dir: Path, object_id: str, candidate_id: str, selection_reason: str) -> None:
    qa_path = package_dir / "qa_report.md"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "",
        "## Candidate Promotion",
        "",
        f"- Time: {timestamp}",
        f"- Object: {object_id}",
        f"- Selected candidate: {candidate_id}",
        f"- Selection reason: {selection_reason}",
    ]
    existing = qa_path.read_text(encoding="utf-8") if qa_path.exists() else ""
    qa_path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def load_compare_manifest(package_dir: Path, relative_path: str, parser: argparse.ArgumentParser) -> dict:
    compare_manifest_path = package_path(package_dir, relative_path, "compare_manifest_path", parser)
    if not compare_manifest_path.exists():
        parser.error(f"compare manifest is missing: {relative_path}")
    try:
        data = json.loads(compare_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        parser.error(f"compare manifest is not valid JSON: {exc}")
    if not isinstance(data, dict):
        parser.error("compare manifest must contain an object")
    return data


def find_compare_candidate_record(compare_manifest: dict, candidate_id: str) -> dict:
    candidates = compare_manifest.get("candidates", [])
    if not isinstance(candidates, list):
        return {}
    for item in candidates:
        if isinstance(item, dict) and item.get("candidate_id") == candidate_id:
            return item
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a staged repair candidate into the package asset inventory."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True, help="Object id to promote.")
    parser.add_argument(
        "--candidate-asset",
        help="Package-relative staged candidate asset path. Optional when --comparison-id can resolve the candidate from compare evidence.",
    )
    parser.add_argument("--candidate-mask", help="Package-relative staged candidate mask path.")
    parser.add_argument("--candidate-id", help="Candidate identifier recorded in metadata. Optional when --comparison-id resolves exactly one candidate.")
    parser.add_argument("--comparison-id", help="Existing candidate comparison record id to resolve.")
    parser.add_argument(
        "--delivery-class",
        choices=[
            "clean-extraction",
            "approximate-reconstruction",
            "generated-reconstruction",
            "support-only",
            "draft-candidate",
        ],
        required=True,
    )
    parser.add_argument("--active-reconstruction-method", default="")
    parser.add_argument("--generation-source", default="")
    parser.add_argument("--generation-model-or-tool", default="")
    parser.add_argument("--generation-version", default="")
    parser.add_argument("--generation-prompt-or-brief-ref", default="")
    parser.add_argument("--generation-reference-input", action="append", default=[])
    parser.add_argument("--repair-note", required=True)
    parser.add_argument("--selection-reason", required=True)
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    metadata = read_metadata(package_dir)
    objects = metadata.get("objects", [])
    target = next(
        (item for item in objects if isinstance(item, dict) and item.get("id") == args.object_id),
        None,
    )
    if target is None:
        parser.error(f"unknown object-id: {args.object_id}")

    comparisons = target.setdefault("candidate_comparisons", [])
    if not isinstance(comparisons, list):
        parser.error("target object candidate_comparisons must be a list when present")
    comparison = None
    compare_manifest = {}
    compare_candidate_record = {}
    candidate_id_value = args.candidate_id or ""
    if args.comparison_id:
        comparison = next(
            (
                item
                for item in comparisons
                if isinstance(item, dict) and item.get("comparison_id") == args.comparison_id
            ),
            None,
        )
        if comparison is None:
            parser.error(f"unknown comparison-id: {args.comparison_id}")
        candidate_ids = comparison.get("candidate_ids", [])
        if not isinstance(candidate_ids, list):
            parser.error("comparison-id must reference a comparison with candidate_ids")
        compare_manifest_path = comparison.get("compare_manifest_path", "")
        if not isinstance(compare_manifest_path, str) or not compare_manifest_path.strip():
            parser.error("comparison-id must reference a comparison with compare_manifest_path")
        compare_manifest = load_compare_manifest(package_dir, compare_manifest_path, parser)
        if not all(
            isinstance(item, str) and item.strip() for item in candidate_ids
        ):
            parser.error("comparison-id must reference a comparison with candidate_ids")
        if not candidate_id_value:
            if len(candidate_ids) == 1:
                candidate_id_value = candidate_ids[0]
            else:
                parser.error("--candidate-id is required when --comparison-id references multiple candidates")
        if candidate_id_value not in candidate_ids:
            parser.error("comparison-id must reference a comparison that includes the selected candidate")
        compare_candidate_record = find_compare_candidate_record(compare_manifest, candidate_id_value)
        if not compare_candidate_record:
            parser.error("comparison-id compare manifest must include the selected candidate record")

    if not candidate_id_value:
        parser.error("--candidate-id is required unless --comparison-id resolves exactly one candidate")

    candidate_asset_value = args.candidate_asset
    if not candidate_asset_value and compare_candidate_record:
        candidate_asset_value = str(compare_candidate_record.get("asset_path", "")).strip()
    if not candidate_asset_value:
        parser.error("--candidate-asset is required unless --comparison-id resolves the candidate asset from compare evidence")

    candidate_asset = package_path(package_dir, candidate_asset_value, "candidate asset", parser)
    require_repair_candidate_path(candidate_asset, package_dir, "candidate asset", parser)
    if not candidate_asset.exists():
        parser.error(f"candidate asset is missing: {candidate_asset}")

    current_asset_path = target.get("asset_path")
    if not isinstance(current_asset_path, str) or not current_asset_path.strip():
        parser.error("target object is missing asset_path")
    destination_asset = package_path(
        package_dir, current_asset_path, "target asset_path", parser
    )
    destination_asset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate_asset, destination_asset)

    if args.candidate_mask:
        candidate_mask = package_path(
            package_dir, args.candidate_mask, "candidate mask", parser
        )
        require_repair_candidate_path(candidate_mask, package_dir, "candidate mask", parser)
        if not candidate_mask.exists():
            parser.error(f"candidate mask is missing: {candidate_mask}")
        current_mask_path = target.get("mask_path")
        if not isinstance(current_mask_path, str) or not current_mask_path.strip():
            parser.error("target object is missing mask_path")
        destination_mask = package_path(
            package_dir, current_mask_path, "target mask_path", parser
        )
        destination_mask.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidate_mask, destination_mask)

    try:
        provider_stage = load_provider_stage_manifest(candidate_asset, candidate_id_value)
    except (ValueError, json.JSONDecodeError) as exc:
        parser.error(f"provider stage manifest is not valid JSON: {exc}")

    target["selected_candidate_id"] = candidate_id_value
    target["current_asset_revision"] = candidate_id_value
    target["delivery_class"] = args.delivery_class
    if args.delivery_class == "approximate-reconstruction":
        target["reuse_status"] = "approximate-reconstruction"
        target["approximate"] = True
    if args.delivery_class == "generated-reconstruction":
        generation_source = (
            args.generation_source
            or str(compare_candidate_record.get("generation_source", "")).strip()
            or str(provider_stage.get("generation_source", "")).strip()
        )
        generation_model_or_tool = (
            args.generation_model_or_tool
            or str(compare_candidate_record.get("generation_model_or_tool", "")).strip()
            or str(provider_stage.get("generation_model_or_tool", "")).strip()
        )
        generation_version = (
            args.generation_version
            or str(compare_candidate_record.get("generation_version", "")).strip()
            or str(provider_stage.get("generation_version", "")).strip()
        )
        generation_prompt_or_brief_ref = (
            args.generation_prompt_or_brief_ref
            or str(compare_candidate_record.get("generation_prompt_or_brief_ref", "")).strip()
            or str(provider_stage.get("generation_prompt_or_brief_ref", "")).strip()
        )
        generation_reference_inputs = (
            list(args.generation_reference_input)
            or list(
                compare_candidate_record.get("generation_reference_inputs", [])
                if isinstance(compare_candidate_record.get("generation_reference_inputs", []), list)
                else []
            )
            or list(
                provider_stage.get("generation_reference_inputs", [])
                if isinstance(provider_stage.get("generation_reference_inputs", []), list)
                else []
            )
        )
        if not generation_source:
            parser.error(
                "generated-reconstruction promotion requires generation_source or a provider stage manifest with generation_source"
            )
        if not generation_model_or_tool:
            parser.error(
                "generated-reconstruction promotion requires generation_model_or_tool or a provider stage manifest with generation_model_or_tool"
            )
        if not generation_prompt_or_brief_ref:
            parser.error(
                "generated-reconstruction promotion requires generation_prompt_or_brief_ref or a provider stage manifest with generation_prompt_or_brief_ref"
            )
        if not generation_reference_inputs:
            parser.error(
                "generated-reconstruction promotion requires generation_reference_inputs or a provider stage manifest with generation_reference_inputs"
            )
        target["generation_source"] = generation_source
        target["generation_model_or_tool"] = generation_model_or_tool
        target["generation_version"] = generation_version
        target["generation_prompt_or_brief_ref"] = generation_prompt_or_brief_ref
        target["generation_reference_inputs"] = generation_reference_inputs
    target["active_reconstruction_method"] = args.active_reconstruction_method
    repair_history = target.setdefault("repair_history", [])
    repair_history.append(
        {
            "candidate_id": candidate_id_value,
            "note": args.repair_note,
            "candidate_asset": candidate_asset_value,
            "candidate_mask": args.candidate_mask or "",
            "selection_reason": args.selection_reason,
            "comparison_id": args.comparison_id or "",
        }
    )
    if args.comparison_id:
        comparison["selected_candidate_id"] = candidate_id_value
        comparison["selection_reason"] = args.selection_reason
        comparison["selected_at"] = now
    else:
        comparison_id = f"manual-{candidate_id_value}"
        compare_manifest_rel = f"_staging/repair_candidates/{comparison_id}_compare.json"
        write_json(
            package_dir / compare_manifest_rel,
            {
                "comparison_id": comparison_id,
                "object_id": args.object_id,
                "candidate_ids": [candidate_id_value],
                "candidates": [
                    {
                        "candidate_id": candidate_id_value,
                        "asset_path": candidate_asset_value,
                    }
                ],
                "compare_artifact_path": "",
                "compare_note": "Manual direct promotion without multi-candidate comparison.",
                "compare_criteria": ["single-candidate direct promotion"],
                "review_focus": ["selection rationale"],
                "risks": [],
                "score_manifest_path": "",
                "created_at": now,
            },
        )
        compare_manifest_data = json.loads((package_dir / compare_manifest_rel).read_text(encoding="utf-8"))
        if args.delivery_class == "generated-reconstruction" and provider_stage:
            compare_manifest_data["candidates"][0]["provider_stage_manifest_path"] = str(
                (candidate_asset.parent / f"{candidate_id_value}_provider_stage.json").relative_to(package_dir)
            ).replace("\\", "/")
            compare_manifest_data["candidates"][0]["provider_id"] = provider_stage.get("provider_id", "")
            compare_manifest_data["candidates"][0]["provider_request_path"] = provider_stage.get(
                "provider_request_path", ""
            )
            compare_manifest_data["candidates"][0]["provider_result_path"] = provider_stage.get(
                "provider_result_path", ""
            )
            for field_name in [
                "generation_source",
                "generation_model_or_tool",
                "generation_version",
                "generation_prompt_or_brief_ref",
                "generation_reference_inputs",
            ]:
                compare_manifest_data["candidates"][0][field_name] = provider_stage.get(
                    field_name,
                    [] if field_name == "generation_reference_inputs" else "",
                )
            write_json(package_dir / compare_manifest_rel, compare_manifest_data)
        comparisons.append(
            {
                "comparison_id": comparison_id,
                "object_id": args.object_id,
                "candidate_ids": [candidate_id_value],
                "compare_artifact_path": "",
                "compare_manifest_path": compare_manifest_rel,
                "compare_note": "Manual direct promotion without multi-candidate comparison.",
                "compare_criteria": ["single-candidate direct promotion"],
                "review_focus": ["selection rationale"],
                "risks": [],
                "score_manifest_path": "",
                "selected_candidate_id": candidate_id_value,
                "selection_reason": args.selection_reason,
                "created_at": now,
            }
        )
    update_asset_summary(metadata)
    write_metadata(package_dir, metadata)
    append_qa_report(package_dir, args.object_id, candidate_id_value, args.selection_reason)
    print(f"Promoted candidate {candidate_id_value} for {args.object_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
