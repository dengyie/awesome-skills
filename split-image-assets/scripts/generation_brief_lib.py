import json
from pathlib import Path

from package_state_lib import find_plan_object, read_plan_manifest
from split_image_assets_contract import default_generation_brief


def _relative_package_path(package_dir: Path, value: str, label: str) -> str:
    candidate = Path(value)
    if candidate.is_absolute():
        raise ValueError(f"{label} must be a package-relative path")
    resolved = (package_dir / candidate).resolve()
    package_root = package_dir.resolve()
    if resolved != package_root and package_root not in resolved.parents:
        raise ValueError(f"{label} must stay inside the package")
    return str(candidate).replace("\\", "/")


def generation_brief_dir(package_dir: Path) -> Path:
    return package_dir / "_staging" / "generation_briefs"


def generation_brief_path(package_dir: Path, object_id: str) -> Path:
    return generation_brief_dir(package_dir) / f"{object_id}.json"


def generation_reference_inputs_path(package_dir: Path, object_id: str) -> Path:
    return generation_brief_dir(package_dir) / f"{object_id}_reference_inputs.json"


def _auto_planning_path(package_dir: Path, object_id: str, suffix: str) -> str:
    candidate = package_dir / "_staging" / "planning" / f"{object_id}_{suffix}.png"
    if candidate.exists():
        return str(candidate.relative_to(package_dir)).replace("\\", "/")
    return ""


def _default_reference_inputs(package_dir: Path) -> list[str]:
    source_original = package_dir / "source" / "source_original.png"
    if source_original.exists():
        return ["source/source_original.png"]
    return []


def build_generation_brief(
    package_dir: Path,
    object_id: str,
    *,
    source_crop: str = "",
    rough_mask: str = "",
    rough_localization: str = "",
    neighbor_context: str = "",
    style_constraints: list[str] | None = None,
    must_keep: list[str] | None = None,
    must_avoid: list[str] | None = None,
    reference_inputs: list[str] | None = None,
    why_not_extract: str = "",
    why_not_reconstruct: str = "",
    why_generate: str = "",
    risk_note: str = "",
) -> tuple[dict, dict]:
    plan_manifest = read_plan_manifest(package_dir)
    if plan_manifest is None:
        raise ValueError("plan_manifest.json must exist before preparing a generation brief")
    plan_object = find_plan_object(plan_manifest, object_id)
    if plan_object is None:
        raise ValueError(f"plan_manifest.json is missing object_id: {object_id}")
    planned_route = str(plan_object.get("planned_route", "")).strip()
    if planned_route != "generate":
        raise ValueError(
            f"generation briefs are only valid for planned_route=generate; {object_id} is {planned_route or 'unset'}"
        )
    object_type = str(plan_object.get("object_type", "generic-object")).strip() or "generic-object"
    brief = default_generation_brief(object_id, object_type)

    brief["source_crop"] = _relative_package_path(package_dir, source_crop, "source_crop") if source_crop else _auto_planning_path(package_dir, object_id, "crop")
    brief["rough_mask"] = _relative_package_path(package_dir, rough_mask, "rough_mask") if rough_mask else _auto_planning_path(package_dir, object_id, "mask")
    brief["rough_localization"] = (
        _relative_package_path(package_dir, rough_localization, "rough_localization")
        if rough_localization
        else ""
    )
    brief["neighbor_context"] = (
        _relative_package_path(package_dir, neighbor_context, "neighbor_context")
        if neighbor_context
        else ""
    )
    brief["style_constraints"] = list(style_constraints or [])
    brief["must_keep"] = list(must_keep or [])
    brief["must_avoid"] = list(must_avoid or [])
    brief["why_not_extract"] = why_not_extract or str(plan_object.get("why_not_extract", "")).strip()
    brief["why_not_reconstruct"] = why_not_reconstruct or str(plan_object.get("why_not_reconstruct", "")).strip()
    brief["why_generate"] = why_generate or str(plan_object.get("why_generate", "")).strip()
    brief["risk_note"] = risk_note or str(plan_object.get("risk_note", "")).strip()

    normalized_reference_inputs: list[str] = []
    for value in list(reference_inputs or _default_reference_inputs(package_dir)):
        normalized = _relative_package_path(package_dir, value, "reference_input")
        if normalized not in normalized_reference_inputs:
            normalized_reference_inputs.append(normalized)

    reference_manifest = {
        "object_id": object_id,
        "reference_inputs": normalized_reference_inputs,
    }
    return brief, reference_manifest


def write_generation_brief(
    package_dir: Path,
    object_id: str,
    brief: dict,
    reference_manifest: dict,
) -> tuple[Path, Path]:
    brief_dir = generation_brief_dir(package_dir)
    brief_dir.mkdir(parents=True, exist_ok=True)
    brief_path = generation_brief_path(package_dir, object_id)
    references_path = generation_reference_inputs_path(package_dir, object_id)
    brief_path.write_text(
        json.dumps(brief, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    references_path.write_text(
        json.dumps(reference_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return brief_path, references_path
