from pathlib import Path


PROVIDER_REQUEST_SCHEMA_VERSION = "1.0"
PROVIDER_RESULT_SCHEMA_VERSION = "1.0"

ALLOWED_PROVIDER_EXECUTION_MODES = {
    "bridge",
    "external-manifest",
    "host-managed",
    "native",
}

ALLOWED_PROVIDER_ROLES = {
    "detection",
    "segmentation",
    "matting",
    "reconstruction",
    "generation",
}

ALLOWED_PROVIDER_RESULT_STATUSES = {
    "success",
    "partial",
    "failed",
    "blocked",
}

REQUIRED_PROVIDER_REQUEST_FIELDS = {
    "schema_version",
    "package_name",
    "provider_id",
    "provider_role",
    "execution_mode",
    "object_id",
    "object_type",
    "planned_route",
    "quality_target",
    "source_image",
    "input_refs",
    "expected_outputs",
    "notes",
}

REQUIRED_PROVIDER_RESULT_FIELDS = {
    "schema_version",
    "package_name",
    "provider_id",
    "provider_role",
    "execution_mode",
    "object_id",
    "status",
    "artifacts",
    "provenance",
    "warnings",
    "production_ready_hint",
    "next_expected_provider",
    "notes",
}


def _resolve_package_relative_path(package_dir: Path, value: str, label: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        raise ValueError(f"{label} must be a package-relative path")
    resolved = (package_dir / candidate).resolve()
    package_root = package_dir.resolve()
    if resolved != package_root and package_root not in resolved.parents:
        raise ValueError(f"{label} must stay inside the package")
    return resolved


def validate_provider_request(package_dir: Path, request: dict) -> None:
    if not isinstance(request, dict):
        raise ValueError("provider request must be an object")
    missing = sorted(REQUIRED_PROVIDER_REQUEST_FIELDS - set(request))
    if missing:
        raise ValueError("provider request missing required fields: " + ", ".join(missing))
    if request.get("schema_version") != PROVIDER_REQUEST_SCHEMA_VERSION:
        raise ValueError("provider request schema_version must be 1.0")
    if request.get("execution_mode") not in ALLOWED_PROVIDER_EXECUTION_MODES:
        raise ValueError("provider request execution_mode is invalid")
    if request.get("provider_role") not in ALLOWED_PROVIDER_ROLES:
        raise ValueError("provider request provider_role is invalid")
    for field_name in ["package_name", "provider_id", "object_id", "object_type", "planned_route", "quality_target"]:
        value = request.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"provider request {field_name} must be a non-empty string")
    source_image = request.get("source_image")
    if not isinstance(source_image, str) or not source_image.strip():
        raise ValueError("provider request source_image must be a non-empty package-relative path")
    _resolve_package_relative_path(package_dir, source_image, "provider request source_image")
    input_refs = request.get("input_refs")
    if not isinstance(input_refs, dict):
        raise ValueError("provider request input_refs must be an object")
    for key, value in input_refs.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("provider request input_refs keys must be non-empty strings")
        if value in ("", None):
            continue
        if not isinstance(value, str):
            raise ValueError(f"provider request input_refs.{key} must be a string when present")
        _resolve_package_relative_path(package_dir, value, f"provider request input_refs.{key}")
    expected_outputs = request.get("expected_outputs")
    if not isinstance(expected_outputs, dict) or not expected_outputs:
        raise ValueError("provider request expected_outputs must be a non-empty object")
    for key, value in expected_outputs.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("provider request expected_outputs keys must be non-empty strings")
        if not isinstance(value, bool):
            raise ValueError(f"provider request expected_outputs.{key} must be true or false")
    notes = request.get("notes")
    if not isinstance(notes, str):
        raise ValueError("provider request notes must be a string")


def validate_provider_result(package_dir: Path, result: dict) -> None:
    if not isinstance(result, dict):
        raise ValueError("provider result must be an object")
    missing = sorted(REQUIRED_PROVIDER_RESULT_FIELDS - set(result))
    if missing:
        raise ValueError("provider result missing required fields: " + ", ".join(missing))
    if result.get("schema_version") != PROVIDER_RESULT_SCHEMA_VERSION:
        raise ValueError("provider result schema_version must be 1.0")
    if result.get("execution_mode") not in ALLOWED_PROVIDER_EXECUTION_MODES:
        raise ValueError("provider result execution_mode is invalid")
    if result.get("provider_role") not in ALLOWED_PROVIDER_ROLES:
        raise ValueError("provider result provider_role is invalid")
    if result.get("status") not in ALLOWED_PROVIDER_RESULT_STATUSES:
        raise ValueError("provider result status is invalid")
    for field_name in ["package_name", "provider_id", "object_id"]:
        value = result.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"provider result {field_name} must be a non-empty string")
    artifacts = result.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("provider result artifacts must be an object")
    for key, value in artifacts.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("provider result artifact keys must be non-empty strings")
        if value in ("", None):
            continue
        if not isinstance(value, str):
            raise ValueError(f"provider result artifacts.{key} must be a string when present")
        _resolve_package_relative_path(package_dir, value, f"provider result artifacts.{key}")
    provenance = result.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("provider result provenance must be an object")
    for field_name in ["tool_name", "tool_role", "tool_version", "execution_mode"]:
        value = provenance.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"provider result provenance.{field_name} must be a non-empty string")
    warnings = result.get("warnings")
    if not isinstance(warnings, list) or not all(isinstance(item, str) for item in warnings):
        raise ValueError("provider result warnings must be a list of strings")
    if not isinstance(result.get("production_ready_hint"), bool):
        raise ValueError("provider result production_ready_hint must be true or false")
    next_expected_provider = result.get("next_expected_provider")
    if next_expected_provider is not None and not isinstance(next_expected_provider, str):
        raise ValueError("provider result next_expected_provider must be a string")
    notes = result.get("notes")
    if not isinstance(notes, str):
        raise ValueError("provider result notes must be a string")
