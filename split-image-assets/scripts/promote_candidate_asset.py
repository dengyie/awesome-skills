import argparse
import json
import shutil
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a staged repair candidate into the package asset inventory."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True, help="Object id to promote.")
    parser.add_argument("--candidate-asset", required=True, help="Package-relative staged candidate asset path.")
    parser.add_argument("--candidate-mask", help="Package-relative staged candidate mask path.")
    parser.add_argument("--candidate-id", required=True, help="Candidate identifier recorded in metadata.")
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
        }
    )
    update_asset_summary(metadata)
    write_metadata(package_dir, metadata)
    print(f"Promoted candidate {args.candidate_id} for {args.object_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
