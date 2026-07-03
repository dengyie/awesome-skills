import json
from pathlib import Path

from package_state_lib import find_plan_object, read_plan_manifest
from provider_contract import (
    PROVIDER_REQUEST_SCHEMA_VERSION,
    PROVIDER_RESULT_SCHEMA_VERSION,
    validate_provider_request,
    validate_provider_result,
)
from provider_registry import get_provider_spec


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


def build_provider_request(
    package_dir: Path,
    object_id: str,
    provider_id: str,
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
    provider_spec = get_provider_spec(provider_id)
    planned_route = str(plan_object.get("planned_route", "")).strip()
    if planned_route not in provider_spec["supported_routes"]:
        raise ValueError(
            f"provider {provider_id} does not support planned route: {planned_route}"
        )
    source = metadata.get("source", {})
    quality_target = plan_manifest.get("quality_target", {})
    request = {
        "schema_version": PROVIDER_REQUEST_SCHEMA_VERSION,
        "package_name": metadata.get("package_name", ""),
        "provider_id": provider_spec["provider_id"],
        "provider_role": provider_spec["provider_role"],
        "execution_mode": provider_spec["execution_mode"],
        "object_id": object_id,
        "object_type": str(plan_object.get("object_type", "")).strip(),
        "planned_route": planned_route,
        "quality_target": str(quality_target.get("tier", "")).strip(),
        "source_image": str(source.get("path", "")).strip(),
        "input_refs": input_refs or {},
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
