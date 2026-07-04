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
from provider_registry import (
    get_default_provider_chain,
    get_default_route_chain,
    get_object_type_override_chain,
    get_provider_spec,
    list_supported_provider_ids,
)


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
    if not isinstance(candidate, str):
        return ""
    normalized = candidate.strip()
    if normalized in {"", "unset"}:
        return ""
    return normalized


def describe_provider_selection(
    plan_manifest: dict,
    planned_route: str,
    object_type: str,
    provider_id: str | None,
) -> dict:
    route = str(planned_route).strip()
    obj_type = str(object_type).strip()
    explicit = provider_id.strip() if isinstance(provider_id, str) and provider_id.strip() else ""
    preferred = _preferred_provider_id(plan_manifest, route)
    route_default_chain = get_default_route_chain(route)
    object_type_override_chain = get_object_type_override_chain(route, obj_type)
    selected_default_chain = get_default_provider_chain(route, obj_type)
    supported_provider_ids = list_supported_provider_ids(route)
    selection_source = "route-default"
    selected_provider_id = selected_default_chain[0] if selected_default_chain else ""
    preferred_status = "not-set"
    notes: list[str] = []

    if explicit:
        get_provider_spec(explicit)
        selection_source = "explicit-provider-id"
        selected_provider_id = explicit
        if preferred:
            preferred_status = "overridden-by-explicit"
        notes.append("Explicit provider selection overrides route defaults and plan preferences.")
    elif preferred:
        try:
            preferred_spec = get_provider_spec(preferred)
        except ValueError:
            preferred_status = "invalid-provider-id"
            notes.append(
                f"Plan preference {preferred!r} is not registered; the default provider chain will be used."
            )
        else:
            if route not in preferred_spec["supported_routes"]:
                preferred_status = "unsupported-route"
                notes.append(
                    f"Plan preference {preferred!r} does not support planned route {route!r}; the default provider chain will be used."
                )
            else:
                preferred_status = "applied"
                selection_source = "plan-preference"
                selected_provider_id = preferred
    elif object_type_override_chain:
        selection_source = "object-type-override"

    provider_spec = get_provider_spec(selected_provider_id) if selected_provider_id else None
    alternative_provider_chain = [
        candidate_id for candidate_id in supported_provider_ids if candidate_id != selected_provider_id
    ]
    if selection_source == "object-type-override":
        notes.append(
            f"Object type {obj_type!r} overrides the route default provider chain for planned route {route!r}."
        )
    elif selection_source == "route-default" and selected_provider_id:
        notes.append(f"Using the route default provider chain for planned route {route!r}.")
    elif selection_source == "plan-preference":
        notes.append("A valid plan preference overrides the normal default provider chain.")

    return {
        "planned_route": route,
        "object_type": obj_type,
        "selected_provider_id": selected_provider_id,
        "selection_source": selection_source,
        "preferred_provider_id": preferred,
        "preferred_provider_status": preferred_status,
        "route_default_chain": route_default_chain,
        "object_type_override_chain": object_type_override_chain,
        "selected_provider_chain": [selected_provider_id] if selected_provider_id else [],
        "alternative_provider_chain": alternative_provider_chain,
        "provider_role": provider_spec["provider_role"] if provider_spec else "",
        "execution_mode": provider_spec["execution_mode"] if provider_spec else "",
        "notes": notes,
    }


def resolve_provider_id(plan_manifest: dict, planned_route: str, object_type: str, provider_id: str | None) -> str:
    selection = describe_provider_selection(plan_manifest, planned_route, object_type, provider_id)
    selected_provider_id = str(selection.get("selected_provider_id", "")).strip()
    if selected_provider_id:
        return selected_provider_id
    raise ValueError(
        f"cannot resolve provider id for planned route {planned_route!r} and object type {object_type!r}"
    )


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


def build_provider_plan_summary(package_dir: Path, object_id: str | None = None) -> dict:
    metadata = _load_metadata(package_dir)
    plan_manifest = read_plan_manifest(package_dir)
    if plan_manifest is None:
        raise ValueError("plan_manifest.json must exist before building a provider plan summary")
    objects = plan_manifest.get("objects", [])
    if not isinstance(objects, list):
        raise ValueError("plan_manifest.json objects must be a list")

    requested_object_id = object_id.strip() if isinstance(object_id, str) and object_id.strip() else ""
    summary_objects: list[dict] = []
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        current_object_id = str(obj.get("object_id", "")).strip()
        if not current_object_id:
            continue
        if requested_object_id and current_object_id != requested_object_id:
            continue
        planned_route = str(obj.get("planned_route", "")).strip()
        object_type = str(obj.get("object_type", "")).strip()
        selection = describe_provider_selection(plan_manifest, planned_route, object_type, None)
        summary_objects.append(
            {
                "object_id": current_object_id,
                **selection,
            }
        )

    if requested_object_id and not summary_objects:
        raise ValueError(f"plan_manifest.json is missing object_id: {requested_object_id}")

    return {
        "schema_version": "1.0",
        "package_name": str(metadata.get("package_name", "")).strip(),
        "provider_preferences": plan_manifest.get("provider_preferences", {}),
        "objects": summary_objects,
    }


def write_provider_plan_summary(package_dir: Path, summary: dict) -> Path:
    target = provider_bridge_root(package_dir) / "provider_plan.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target


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


def load_provider_request(package_dir: Path, provider_id: str, object_id: str) -> dict:
    path = provider_request_path(package_dir, provider_id, object_id)
    if not path.exists():
        raise ValueError(f"provider request is missing: {path}")
    request = json.loads(path.read_text(encoding="utf-8"))
    validate_provider_request(package_dir, request)
    return request


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
