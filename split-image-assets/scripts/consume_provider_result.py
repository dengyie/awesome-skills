import argparse
import json
import shutil
from pathlib import Path

from import_external_assets import checked_metadata, import_record, load_manifest
from provider_bridge_lib import load_provider_result


def stage_generated_candidate(
    package_dir: Path,
    parser: argparse.ArgumentParser,
    result: dict,
    object_id: str,
    candidate_id: str,
) -> None:
    artifacts = result.get("artifacts", {})
    candidate_path = artifacts.get("candidate_png") or artifacts.get("compare_ready_candidate")
    if not isinstance(candidate_path, str) or not candidate_path.strip():
        parser.error("provider result must include candidate_png or compare_ready_candidate for stage-candidate")
    source = (package_dir / candidate_path).resolve()
    if not source.exists():
        parser.error(f"provider candidate artifact is missing: {candidate_path}")
    target_dir = package_dir / "_staging" / "repair_candidates" / object_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_asset = target_dir / f"{candidate_id}.png"
    shutil.copy2(source, target_asset)
    manifest_path = target_dir / f"{candidate_id}_provider_stage.json"
    manifest_path.write_text(
        json.dumps(
            {
                "object_id": object_id,
                "candidate_id": candidate_id,
                "provider_id": result.get("provider_id", ""),
                "provider_result_path": f"_staging/providers/{result.get('provider_id', '')}/{object_id}/result.json",
                "staged_candidate_path": str(target_asset.relative_to(package_dir)).replace("\\", "/"),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Consume a provider bridge result through an explicit package-owned entrypoint.")
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--provider-id", required=True)
    parser.add_argument("--object-id", required=True)
    parser.add_argument(
        "--mode",
        required=True,
        choices=["import-extract", "stage-candidate", "import-manifest"],
    )
    parser.add_argument("--role", choices=["main", "secondary", "group", "background", "shadow"])
    parser.add_argument("--layer-kind")
    parser.add_argument("--composition-order", type=int)
    parser.add_argument("--semantic-boundary")
    parser.add_argument("--object-type", default="generic-object")
    parser.add_argument("--recipe", default="grounded-segmentation-matting-repair")
    parser.add_argument("--confidence", default="medium", choices=["high", "medium", "low"])
    parser.add_argument("--edge-complexity", default="soft", choices=["hard", "soft", "transparent-reflective"])
    parser.add_argument("--extraction-method", default="ai-assisted", choices=["exact", "ai-assisted", "manual", "estimated", "unknown"])
    parser.add_argument("--candidate-id")
    parser.add_argument("--manifest")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = checked_metadata(package_dir, parser)

    if args.mode == "import-manifest":
        if not args.manifest:
            parser.error("--manifest is required for import-manifest")
        manifest = load_manifest(Path(args.manifest).resolve(), parser)
        subprocess_parser = parser
        tool = manifest.get("tool", {})
        if not isinstance(tool, dict):
            parser.error("manifest.tool must be an object")
        for field in ["name", "role", "version"]:
            value = tool.get(field)
            if not isinstance(value, str) or not value.strip():
                parser.error(f"manifest.tool.{field} is required and must be non-empty")
        objects = manifest.get("objects", [])
        if not isinstance(objects, list) or not objects:
            parser.error("manifest.objects must be a non-empty list")
        for record in objects:
            import_record(
                package_dir,
                metadata,
                subprocess_parser,
                record,
                str(manifest.get("recipe", args.recipe)),
                str(tool.get("name", "")),
                str(tool.get("role", "")),
                str(tool.get("version", "")),
                args.confidence,
                args.edge_complexity,
                args.extraction_method,
            )
        metadata.setdefault("qa", {})["status"] = "needs-review"
    else:
        result = load_provider_result(package_dir, args.provider_id, args.object_id)
        if args.mode == "import-extract":
            missing = [
                name
                for name, value in [
                    ("--role", args.role),
                    ("--layer-kind", args.layer_kind),
                    ("--composition-order", args.composition_order),
                    ("--semantic-boundary", args.semantic_boundary),
                ]
                if value in (None, "")
            ]
            if missing:
                parser.error("import-extract requires: " + ", ".join(missing))
            artifacts = result.get("artifacts", {})
            asset = artifacts.get("asset_png")
            mask = artifacts.get("source_space_mask")
            if not isinstance(asset, str) or not asset.strip():
                parser.error("provider result must include artifacts.asset_png for import-extract")
            if not isinstance(mask, str) or not mask.strip():
                parser.error("provider result must include artifacts.source_space_mask for import-extract")
            provenance = result.get("provenance", {})
            import_record(
                package_dir,
                metadata,
                parser,
                {
                    "object_id": args.object_id,
                    "role": args.role,
                    "layer_kind": args.layer_kind,
                    "composition_order": args.composition_order,
                    "semantic_boundary": args.semantic_boundary,
                    "asset": str((package_dir / asset).resolve()),
                    "mask": str((package_dir / mask).resolve()),
                    "mask_source": args.provider_id,
                    "alpha_source": args.provider_id,
                    "object_type": args.object_type,
                },
                args.recipe,
                str(provenance.get("tool_name", "")),
                str(provenance.get("tool_role", "")),
                str(provenance.get("tool_version", "")),
                args.confidence,
                args.edge_complexity,
                args.extraction_method,
            )
            metadata.setdefault("qa", {})["status"] = "needs-review"
        elif args.mode == "stage-candidate":
            if not args.candidate_id:
                parser.error("--candidate-id is required for stage-candidate")
            stage_generated_candidate(package_dir, parser, result, args.object_id, args.candidate_id)

    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Consumed provider result for {args.object_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
