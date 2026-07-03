import json
from pathlib import Path

from generation_brief_lib import generation_brief_path, generation_reference_inputs_path
from package_state_lib import find_plan_object, read_plan_manifest
from provider_contract import (
    PROVIDER_REQUEST_SCHEMA_VERSION,
    PROVIDER_RESULT_SCHEMA_VERSION,
    validate_provider_request,
    validate_provider_result,
)
from provider_registry import get_default_provider_chain, get_provider_spec


def provider_bridge_root(package_dir: Path) -> Path:
    return package_dir / "_staging" / "providers"


def provider_object_dir(package_dir: Path, provider_id: str, object_id: str) -> Path:
    return provider_bridge_root(package_dir) / provider_id / object_id


def provider_request_path(package_dir: Path, provider_id: str, object_id: str) -> Path:
    return provider_object_dir(package_dir, provider_id, object_id) / "request.json"


def provider_result_path(package_dir: Path, provider_id: str, object_id: str) -> Path:
    return provider_object_dir(package_dir, provider_id, object_id) / "result.json"


def _load_metadata(package_dir: Path) -> dict:
    metadata_path = package_dir / "metadata.json"
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def _preferred_provider_id(plan_manifest: dict, planned_route: str) -> str:
    preferences = plan_manifest.get("provider_preferences", {})
    if not isinstance(preferences, dict):
        return ""
    if planned_route == "generate":
        candidate = preferences.get("generation_provider_class", "")
    else:
        candidate = preferences.get("segmentation_provider_class", "")
    return candidate.strip() if isinstance(candidate, str) else ""


def resolve_provider_id(plan_manifest: dict, planned_route: str, object_type: str, provider_id: str | None) -> str:
    explicit = provider_id.strip() if isinstance(provider_id, str) and provider_id.strip() else ""
    if explicit:
        return explicit
    preferred = _preferred_provider_id(plan_manifest, planned_route)
    if preferred:
        try:
            preferred_spec = get_provider_spec(preferred)
        except ValueError:
            preferred = ""
        else:
            if planned_route in preferred_spec["supported_routes"]:
                return preferred
    return get_default_provider_chain(planned_route, object_type)[0]


def list_staged_result_provider_ids(package_dir: Path, object_id: str) -> list[str]:
    root = provider_bridge_root(package_dir)
    if not root.exists():
        return []
    provider_ids: list[str] = []
    for provider_dir in sorted(root.iterdir()):
        if not provider_dir.is_dir():
            continue
        if provider_result_path(package_dir, provider_dir.name, object_id).exists():
            provider_ids.append(provider_dir.name)
    return provider_ids


def resolve_result_provider_id(package_dir: Path, object_id: str, provider_id: str | None = None) -> str:
    explicit = provider_id.strip() if isinstance(provider_id, str) and provider_id.strip() else ""
    if explicit:
        return explicit

    staged_provider_ids = list_staged_result_provider_ids(package_dir, object_id)
    if len(staged_provider_ids) == 1:
        return staged_provider_ids[0]

    plan_manifest = read_plan_manifest(package_dir)
    preferred = ""
    plan_object = find_plan_object(plan_manifest, object_id)
    if isinstance(plan_manifest, dict) and isinstance(plan_object, dict):
        planned_route = str(plan_object.get("planned_route", "")).strip()
        object_type = str(plan_object.get("object_type", "")).strip()
        if planned_route and object_type:
            preferred = resolve_provider_id(plan_manifest, planned_route, object_type, None)

    if preferred and preferred in staged_provider_ids:
        return preferred

    if len(staged_provider_ids) > 1:
        providers = ", ".join(staged_provider_ids)
        raise ValueError(
            f"multiple staged provider results exist for {object_id}: {providers}; supply --provider-id"
        )

    if preferred:
        return preferred

    raise ValueError(
        f"cannot resolve provider result for {object_id}; supply --provider-id or stage exactly one provider result"
    )


def _augment_generate_input_refs(package_dir: Path, object_id: str, input_refs: dict[str, str]) -> dict[str, str]:
    augmented = dict(input_refs)
    if "generation_brief" not in augmented:
        brief_path = generation_brief_path(package_dir, object_id)
        if not brief_path.exists():
            raise ValueError(
                f"generate route requires a prepared generation brief for {object_id}; run prepare_generation_brief.py first"
            )
        augmented["generation_brief"] = str(brief_path.relative_to(package_dir)).replace("\\", "/")
    if "reference_inputs" not in augmented:
        reference_path = generation_reference_inputs_path(package_dir, object_id)
        if not reference_path.exists():
            raise ValueError(
                f"generate route requires a prepared reference-input manifest for {object_id}; run prepare_generation_brief.py first"
            )
        augmented["reference_inputs"] = str(reference_path.relative_to(package_dir)).replace("\\", "/")
    return augmented


def build_provider_request(
    package_dir: Path,
    object_id: str,
    provider_id: str | None = None,
    *,
    input_refs: dict[str, str] | None = None,
    notes: str = "",
) -> dict:
    metadata = _load_metadata(package_dir)
    plan_manifest = read_plan_manifest(package_dir)
    if plan_manifest is None:
        raise ValueError("plan_manifest.json must exist before building provider requests")
    plan_object = find_plan_object(plan_manifest, object_id)
    if plan_object is None:
        raise ValueError(f"plan_manifest.json is missing object_id: {object_id}")
    planned_route = str(plan_object.get("planned_route", "")).strip()
    object_type = str(plan_object.get("object_type", "")).strip()
    selected_provider_id = resolve_provider_id(plan_manifest, planned_route, object_type, provider_id)
    provider_spec = get_provider_spec(selected_provider_id)
    if planned_route not in provider_spec["supported_routes"]:
        raise ValueError(
            f"provider {selected_provider_id} does not support planned route: {planned_route}"
        )
    normalized_input_refs = dict(input_refs or {})
    if planned_route == "generate":
        normalized_input_refs = _augment_generate_input_refs(package_dir, object_id, normalized_input_refs)
    source = metadata.get("source", {})
    quality_target = plan_manifest.get("quality_target", {})
    request = {
        "schema_version": PROVIDER_REQUEST_SCHEMA_VERSION,
        "package_name": metadata.get("package_name", ""),
        "provider_id": provider_spec["provider_id"],
        "provider_role": provider_spec["provider_role"],
        "execution_mode": provider_spec["execution_mode"],
        "object_id": object_id,
        "object_type": object_type,
        "planned_route": planned_route,
        "quality_target": str(quality_target.get("tier", "")).strip(),
        "source_image": str(source.get("path", "")).strip(),
        "input_refs": normalized_input_refs,
        "expected_outputs": {
            output_name: True for output_name in provider_spec["expected_outputs"]
        },
        "notes": notes,
    }
    validate_provider_request(package_dir, request)
    return request


def write_provider_request(package_dir: Path, request: dict) -> Path:
    validate_provider_request(package_dir, request)
    target = provider_request_path(
        package_dir,
        str(request["provider_id"]),
        str(request["object_id"]),
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(request, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target


def write_provider_result(package_dir: Path, result: dict) -> Path:
    validate_provider_result(package_dir, result)
    target = provider_result_path(
        package_dir,
        str(result["provider_id"]),
        str(result["object_id"]),
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target


def load_provider_result(package_dir: Path, provider_id: str, object_id: str) -> dict:
    path = provider_result_path(package_dir, provider_id, object_id)
    if not path.exists():
        raise ValueError(f"provider result is missing: {path}")
    result = json.loads(path.read_text(encoding="utf-8"))
    validate_provider_result(package_dir, result)
    return result


def build_provider_result(
    package_dir: Path,
    provider_id: str,
    object_id: str,
    *,
    status: str,
    artifacts: dict[str, str],
    tool_name: str,
    tool_role: str,
    tool_version: str,
    execution_mode: str,
    warnings: list[str] | None = None,
    production_ready_hint: bool = False,
    next_expected_provider: str = "",
    notes: str = "",
) -> dict:
    metadata = _load_metadata(package_dir)
    result = {
        "schema_version": PROVIDER_RESULT_SCHEMA_VERSION,
        "package_name": metadata.get("package_name", ""),
        "provider_id": provider_id,
        "provider_role": get_provider_spec(provider_id)["provider_role"],
        "execution_mode": execution_mode,
        "object_id": object_id,
        "status": status,
        "artifacts": artifacts,
        "provenance": {
            "tool_name": tool_name,
            "tool_role": tool_role,
            "tool_version": tool_version,
            "execution_mode": execution_mode,
        },
        "warnings": warnings or [],
        "production_ready_hint": production_ready_hint,
        "next_expected_provider": next_expected_provider,
        "notes": notes,
    }
    validate_provider_result(package_dir, result)
    return result
