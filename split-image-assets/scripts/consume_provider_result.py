import argparse
import json
import shutil
from pathlib import Path

from import_external_assets import checked_metadata, import_record, load_manifest
from provider_bridge_lib import (
    load_provider_request,
    load_provider_result,
    resolve_result_provider_id,
)


def find_metadata_object(metadata: dict, object_id: str) -> dict | None:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        return None
    for item in objects:
        if isinstance(item, dict) and item.get("id") == object_id:
            return item
    return None


def infer_consume_mode(result: dict) -> str:
    artifacts = result.get("artifacts", {})
    matches: list[str] = []
    provider_manifest = artifacts.get("provider_manifest")
    if isinstance(provider_manifest, str) and provider_manifest.strip():
        matches.append("import-manifest")
    asset = artifacts.get("asset_png")
    mask = artifacts.get("source_space_mask")
    if isinstance(asset, str) and asset.strip() and isinstance(mask, str) and mask.strip():
        matches.append("import-extract")
    candidate_path = artifacts.get("candidate_png") or artifacts.get("compare_ready_candidate")
    if isinstance(candidate_path, str) and candidate_path.strip():
        matches.append("stage-candidate")
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if not unique_matches:
        raise ValueError("cannot infer consume mode from provider result artifacts")
    choices = ", ".join(unique_matches)
    raise ValueError(f"cannot infer consume mode because provider result exposes multiple artifact sets: {choices}")


def resolve_import_extract_value(
    cli_value,
    metadata_object: dict | None,
    metadata_key: str,
):
    if cli_value not in (None, ""):
        return cli_value
    if isinstance(metadata_object, dict):
        return metadata_object.get(metadata_key)
    return None


def load_reference_inputs(
    package_dir: Path,
    relative_manifest_path: str,
    parser: argparse.ArgumentParser,
) -> list[str]:
    manifest_path = (package_dir / relative_manifest_path).resolve()
    if not manifest_path.exists():
        parser.error(f"reference_inputs manifest is missing: {relative_manifest_path}")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        parser.error(f"reference_inputs manifest is not valid JSON: {exc}")
    if not isinstance(payload, dict):
        parser.error("reference_inputs manifest must contain an object")
    reference_inputs = payload.get("reference_inputs")
    if not isinstance(reference_inputs, list) or not all(
        isinstance(item, str) and item.strip() for item in reference_inputs
    ):
        parser.error("reference_inputs manifest must contain a non-empty reference_inputs list")
    return list(reference_inputs)


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
    provider_id = str(result.get("provider_id", "")).strip()
    try:
        request = load_provider_request(package_dir, provider_id, object_id)
    except ValueError as exc:
        parser.error(str(exc))
    input_refs = request.get("input_refs", {})
    if not isinstance(input_refs, dict):
        parser.error("provider request input_refs must be an object")
    generation_brief_ref = input_refs.get("generation_brief")
    if not isinstance(generation_brief_ref, str) or not generation_brief_ref.strip():
        parser.error("stage-candidate requires provider request input_refs.generation_brief")
    reference_inputs_ref = input_refs.get("reference_inputs")
    if not isinstance(reference_inputs_ref, str) or not reference_inputs_ref.strip():
        parser.error("stage-candidate requires provider request input_refs.reference_inputs")
    generation_reference_inputs = load_reference_inputs(package_dir, reference_inputs_ref, parser)
    provenance = result.get("provenance", {})
    manifest_path = target_dir / f"{candidate_id}_provider_stage.json"
    manifest_path.write_text(
        json.dumps(
            {
                "object_id": object_id,
                "candidate_id": candidate_id,
                "provider_id": provider_id,
                "provider_request_path": f"_staging/providers/{provider_id}/{object_id}/request.json",
                "provider_result_path": f"_staging/providers/{provider_id}/{object_id}/result.json",
                "staged_candidate_path": str(target_asset.relative_to(package_dir)).replace("\\", "/"),
                "generation_source": provider_id,
                "generation_model_or_tool": str(provenance.get("tool_name", "")),
                "generation_version": str(provenance.get("tool_version", "")),
                "generation_prompt_or_brief_ref": generation_brief_ref,
                "generation_reference_inputs": generation_reference_inputs,
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
    parser.add_argument("--provider-id")
    parser.add_argument("--object-id", required=True)
    parser.add_argument(
        "--mode",
        choices=["import-extract", "stage-candidate", "import-manifest"],
    )
    parser.add_argument("--role", choices=["main", "secondary", "group", "background", "shadow"])
    parser.add_argument("--layer-kind")
    parser.add_argument("--composition-order", type=int)
    parser.add_argument("--semantic-boundary")
    parser.add_argument("--object-type", default="")
    parser.add_argument("--recipe", default="grounded-segmentation-matting-repair")
    parser.add_argument("--confidence", default="medium", choices=["high", "medium", "low"])
    parser.add_argument("--edge-complexity", default="soft", choices=["hard", "soft", "transparent-reflective"])
    parser.add_argument("--extraction-method", default="ai-assisted", choices=["exact", "ai-assisted", "manual", "estimated", "unknown"])
    parser.add_argument("--candidate-id")
    parser.add_argument("--manifest")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = checked_metadata(package_dir, parser)
    metadata_object = find_metadata_object(metadata, args.object_id)
    resolved_provider_id = args.provider_id
    result: dict | None = None

    if args.mode != "import-manifest" or not args.manifest:
        try:
            resolved_provider_id = resolve_result_provider_id(package_dir, args.object_id, args.provider_id)
        except ValueError as exc:
            if args.mode == "import-manifest" and args.manifest:
                resolved_provider_id = args.provider_id
            else:
                parser.error(str(exc))
        if resolved_provider_id:
            try:
                result = load_provider_result(package_dir, resolved_provider_id, args.object_id)
            except ValueError as exc:
                parser.error(str(exc))

    mode = args.mode
    if not mode:
        if result is None:
            parser.error("--mode is required when provider result cannot be loaded for mode inference")
        try:
            mode = infer_consume_mode(result)
        except ValueError as exc:
            parser.error(str(exc))

    if mode == "import-manifest":
        manifest_path: Path | None = None
        if args.manifest:
            manifest_path = Path(args.manifest).resolve()
        else:
            if result is None:
                parser.error("import-manifest requires a provider result or explicit --manifest")
            artifacts = result.get("artifacts", {})
            provider_manifest = artifacts.get("provider_manifest")
            if not isinstance(provider_manifest, str) or not provider_manifest.strip():
                parser.error(
                    "import-manifest requires --manifest or provider result artifacts.provider_manifest"
                )
            manifest_path = (package_dir / provider_manifest).resolve()
        manifest = load_manifest(manifest_path, parser)
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
        if result is None or not resolved_provider_id:
            parser.error("provider result is required for this consume mode")
        if mode == "import-extract":
            role = resolve_import_extract_value(args.role, metadata_object, "role")
            layer_kind = resolve_import_extract_value(args.layer_kind, metadata_object, "layer_kind")
            composition_order = resolve_import_extract_value(
                args.composition_order, metadata_object, "composition_order"
            )
            semantic_boundary = resolve_import_extract_value(
                args.semantic_boundary, metadata_object, "semantic_boundary"
            )
            object_type = resolve_import_extract_value(args.object_type, metadata_object, "object_type")
            missing = [
                name
                for name, value in [
                    ("--role", role),
                    ("--layer-kind", layer_kind),
                    ("--composition-order", composition_order),
                    ("--semantic-boundary", semantic_boundary),
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
                    "role": role,
                    "layer_kind": layer_kind,
                    "composition_order": composition_order,
                    "semantic_boundary": semantic_boundary,
                    "asset": str((package_dir / asset).resolve()),
                    "mask": str((package_dir / mask).resolve()),
                    "mask_source": resolved_provider_id,
                    "alpha_source": resolved_provider_id,
                    "object_type": object_type or "generic-object",
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
        elif mode == "stage-candidate":
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
