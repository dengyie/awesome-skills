import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def read_metadata(package_dir: Path) -> dict:
    return json.loads((package_dir / "metadata.json").read_text(encoding="utf-8"))


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
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


def update_asset_summary(metadata: dict) -> None:
    summary = {
        "production_ready_assets": 0,
        "draft_candidate_assets": 0,
        "support_only_layers": 0,
        "blocked_assets": 0,
    }
    for item in metadata.get("objects", []):
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a staged repair candidate into the package asset inventory."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True, help="Object id to promote.")
    parser.add_argument("--candidate-asset", required=True, help="Package-relative staged candidate asset path.")
    parser.add_argument("--candidate-mask", help="Package-relative staged candidate mask path.")
    parser.add_argument("--candidate-id", required=True, help="Candidate identifier recorded in metadata.")
    parser.add_argument("--comparison-id", help="Existing candidate comparison record id to resolve.")
    parser.add_argument(
        "--delivery-class",
        choices=[
            "clean-extraction",
            "approximate-reconstruction",
            "support-only",
            "draft-candidate",
        ],
        required=True,
    )
    parser.add_argument("--active-reconstruction-method", default="")
    parser.add_argument("--repair-note", required=True)
    parser.add_argument("--selection-reason", required=True)
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = read_metadata(package_dir)
    objects = metadata.get("objects", [])
    target = next(
        (item for item in objects if isinstance(item, dict) and item.get("id") == args.object_id),
        None,
    )
    if target is None:
        parser.error(f"unknown object-id: {args.object_id}")

    candidate_asset = package_path(
        package_dir, args.candidate_asset, "candidate asset", parser
    )
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

    target["selected_candidate_id"] = args.candidate_id
    target["current_asset_revision"] = args.candidate_id
    target["delivery_class"] = args.delivery_class
    if args.delivery_class == "approximate-reconstruction":
        target["reuse_status"] = "approximate-reconstruction"
        target["approximate"] = True
    target["active_reconstruction_method"] = args.active_reconstruction_method
    repair_history = target.setdefault("repair_history", [])
    repair_history.append(
        {
            "candidate_id": args.candidate_id,
            "note": args.repair_note,
            "candidate_asset": args.candidate_asset,
            "candidate_mask": args.candidate_mask or "",
            "selection_reason": args.selection_reason,
            "comparison_id": args.comparison_id or "",
        }
    )
    comparisons = target.setdefault("candidate_comparisons", [])
    if not isinstance(comparisons, list):
        parser.error("target object candidate_comparisons must be a list when present")
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
        if not isinstance(candidate_ids, list) or args.candidate_id not in candidate_ids:
            parser.error("comparison-id must reference a comparison that includes the selected candidate")
        comparison["selected_candidate_id"] = args.candidate_id
        comparison["selection_reason"] = args.selection_reason
        comparison["selected_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        comparisons.append(
            {
                "comparison_id": f"manual-{args.candidate_id}",
                "object_id": args.object_id,
                "candidate_ids": [args.candidate_id],
                "compare_artifact_path": "",
                "compare_manifest_path": "",
                "compare_note": "Manual direct promotion without multi-candidate comparison.",
                "compare_criteria": [],
                "review_focus": [],
                "risks": [],
                "score_manifest_path": "",
                "selected_candidate_id": args.candidate_id,
                "selection_reason": args.selection_reason,
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )
    update_asset_summary(metadata)
    write_metadata(package_dir, metadata)
    append_qa_report(package_dir, args.object_id, args.candidate_id, args.selection_reason)
    print(f"Promoted candidate {args.candidate_id} for {args.object_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
