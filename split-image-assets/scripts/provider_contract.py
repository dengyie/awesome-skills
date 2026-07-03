from pathlib import Path

from provider_registry import get_provider_spec


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

PROVIDER_REQUIRED_REQUEST_INPUTS = {
    "codex-controlled-generation": {"generation_brief", "reference_inputs"},
    "external-generated-outputs": {"generation_brief", "reference_inputs"},
}

PROVIDER_REQUIRED_SUCCESS_OUTPUTS = {
    "grounded-sam-bridge": {"asset_png", "source_space_mask"},
    "external-professional-outputs": {"provider_manifest"},
}

PROVIDER_REQUIRED_SUCCESS_OUTPUT_ALTERNATIVES = {
    "codex-controlled-generation": {"candidate_png", "compare_ready_candidate"},
    "external-generated-outputs": {"candidate_png", "compare_ready_candidate"},
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
    provider_id = str(request.get("provider_id", "")).strip()
    provider_spec = get_provider_spec(provider_id)
    if request.get("provider_role") != provider_spec["provider_role"]:
        raise ValueError("provider request provider_role must match provider registry")
    if request.get("execution_mode") != provider_spec["execution_mode"]:
        raise ValueError("provider request execution_mode must match provider registry")
    planned_route = str(request.get("planned_route", "")).strip()
    if planned_route not in provider_spec["supported_routes"]:
        raise ValueError("provider request planned_route must be supported by the selected provider")
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
    missing_expected_outputs = [
        key for key in provider_spec["expected_outputs"] if expected_outputs.get(key) is not True
    ]
    if missing_expected_outputs:
        raise ValueError(
            "provider request expected_outputs must include provider-required outputs set to true: "
            + ", ".join(missing_expected_outputs)
        )
    required_inputs = PROVIDER_REQUIRED_REQUEST_INPUTS.get(provider_id, set())
    missing_inputs = [
        key
        for key in sorted(required_inputs)
        if not isinstance(input_refs.get(key), str) or not str(input_refs.get(key)).strip()
    ]
    if missing_inputs:
        raise ValueError(
            "provider request input_refs are missing provider-required inputs: "
            + ", ".join(missing_inputs)
        )
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
    provider_id = str(result.get("provider_id", "")).strip()
    provider_spec = get_provider_spec(provider_id)
    if result.get("provider_role") != provider_spec["provider_role"]:
        raise ValueError("provider result provider_role must match provider registry")
    if result.get("execution_mode") != provider_spec["execution_mode"]:
        raise ValueError("provider result execution_mode must match provider registry")
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
    status = result.get("status")
    if status in {"success", "partial"}:
        missing_required_outputs = [
            key
            for key in sorted(PROVIDER_REQUIRED_SUCCESS_OUTPUTS.get(provider_id, set()))
            if not isinstance(artifacts.get(key), str) or not str(artifacts.get(key)).strip()
        ]
        if missing_required_outputs:
            raise ValueError(
                "provider result artifacts are missing provider-required outputs: "
                + ", ".join(missing_required_outputs)
            )
        output_alternatives = PROVIDER_REQUIRED_SUCCESS_OUTPUT_ALTERNATIVES.get(provider_id, set())
        if output_alternatives and not any(
            isinstance(artifacts.get(key), str) and str(artifacts.get(key)).strip()
            for key in output_alternatives
        ):
            raise ValueError(
                "provider result artifacts must include at least one provider-required output: "
                + ", ".join(sorted(output_alternatives))
            )
    if not isinstance(result.get("production_ready_hint"), bool):
        raise ValueError("provider result production_ready_hint must be true or false")
    next_expected_provider = result.get("next_expected_provider")
    if next_expected_provider is not None and not isinstance(next_expected_provider, str):
        raise ValueError("provider result next_expected_provider must be a string")
    notes = result.get("notes")
    if not isinstance(notes, str):
        raise ValueError("provider result notes must be a string")
