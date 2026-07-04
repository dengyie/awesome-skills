V1_ACTIVE_PROVIDER_IDS = {
    "external-professional-outputs",
    "external-generated-outputs",
    "codex-controlled-generation",
    "grounded-sam-bridge",
}

ROUTE_REQUIRED_CAPABILITY_TAGS = {
    "extract": ["source-faithful-extraction", "package-importable-asset"],
    "reconstruct": ["reconstruction-ready-import"],
    "generate": ["brief-driven-generation", "staged-candidate-delivery", "compare-ready-candidate"],
    "rebuild_downstream": [],
    "support_only": [],
}

DEFAULT_ROUTE_PROVIDER_CHAINS = {
    "extract": ["grounded-sam-bridge"],
    "reconstruct": ["external-professional-outputs"],
    "generate": ["codex-controlled-generation"],
    "rebuild_downstream": [],
    "support_only": [],
}

OBJECT_TYPE_PROVIDER_OVERRIDES = {
    ("extract", "photo-object-matte"): ["external-professional-outputs"],
    ("extract", "outlined-illustration-logo"): ["external-professional-outputs"],
}

PROVIDER_REGISTRY = {
    "grounded-sam-bridge": {
        "provider_id": "grounded-sam-bridge",
        "provider_role": "segmentation",
        "execution_mode": "bridge",
        "supported_routes": ["extract"],
        "capability_tags": [
            "source-faithful-extraction",
            "source-space-mask-delivery",
            "package-importable-asset",
        ],
        "preferred_object_types": [
            "ui-glyph",
            "carrier-glyph-pair",
            "flat-support-plate",
            "ui-carrier",
        ],
        "discouraged_object_types": [
            "photo-object-matte",
            "outlined-illustration-logo",
        ],
        "expected_inputs": ["source_image", "source_crop", "rough_mask", "bbox"],
        "expected_outputs": ["asset_png", "source_space_mask"],
        "expected_consume_mode": "import-extract",
        "selection_notes": [
            "Best for bridge-first extraction where a source-space mask plus tight asset import is the main need.",
            "Does not claim hidden-surface reconstruction or alpha-matting refinement by itself.",
        ],
        "production_ready_requires": [
            "source-faithful object mask",
            "package-relative source-space mask",
        ],
    },
    "external-professional-outputs": {
        "provider_id": "external-professional-outputs",
        "provider_role": "segmentation",
        "execution_mode": "external-manifest",
        "supported_routes": ["extract", "reconstruct"],
        "capability_tags": [
            "source-faithful-extraction",
            "package-importable-asset",
            "reconstruction-ready-import",
            "provider-manifest-import",
        ],
        "preferred_object_types": [
            "photo-object-matte",
            "outlined-illustration-logo",
            "soft-edge-logo-brand-mark",
            "occluded-carrier-reconstruction",
        ],
        "discouraged_object_types": [],
        "expected_inputs": ["provider_manifest"],
        "expected_outputs": ["provider_manifest"],
        "expected_consume_mode": "import-manifest",
        "selection_notes": [
            "Best when a mature upstream tool or manual workflow already produced package-importable assets or reconstruction outputs.",
            "Keeps provenance and multi-object import evidence stronger than ad hoc local bridge artifacts.",
        ],
        "production_ready_requires": [
            "importable external provenance",
            "package-owned copied artifacts",
        ],
    },
    "codex-controlled-generation": {
        "provider_id": "codex-controlled-generation",
        "provider_role": "generation",
        "execution_mode": "host-managed",
        "supported_routes": ["generate"],
        "capability_tags": [
            "brief-driven-generation",
            "staged-candidate-delivery",
            "compare-ready-candidate",
        ],
        "preferred_object_types": [
            "ui-carrier",
            "occluded-carrier-reconstruction",
            "flat-support-plate",
        ],
        "discouraged_object_types": [
            "photo-object-matte",
        ],
        "expected_inputs": ["generation_brief", "reference_inputs"],
        "expected_outputs": ["candidate_png", "compare_ready_candidate"],
        "expected_consume_mode": "stage-candidate",
        "selection_notes": [
            "Use when the route is already generate and the package can stay honest about candidate comparison and promotion.",
            "Not a shortcut around extraction truth for source-faithful matte objects.",
        ],
        "production_ready_requires": [
            "object-level constrained generation",
            "transparent asset delivery",
            "compare and promotion evidence",
        ],
    },
    "external-generated-outputs": {
        "provider_id": "external-generated-outputs",
        "provider_role": "generation",
        "execution_mode": "external-manifest",
        "supported_routes": ["generate"],
        "capability_tags": [
            "brief-driven-generation",
            "staged-candidate-delivery",
            "compare-ready-candidate",
            "provider-manifest-import",
        ],
        "preferred_object_types": [
            "ui-carrier",
            "occluded-carrier-reconstruction",
            "flat-support-plate",
        ],
        "discouraged_object_types": [
            "photo-object-matte",
        ],
        "expected_inputs": ["generation_brief", "reference_inputs"],
        "expected_outputs": ["candidate_png", "compare_ready_candidate"],
        "expected_consume_mode": "stage-candidate",
        "selection_notes": [
            "Best when generation runs outside the skill but should still re-enter through the same brief-first candidate workflow.",
            "Still requires compare and promotion evidence before reusable delivery claims.",
        ],
        "production_ready_requires": [
            "transparent generated asset delivery",
            "compare and promotion evidence",
        ],
    },
}


def _normalize_string_list(values: list[str] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values or []:
        if not isinstance(item, str):
            continue
        candidate = item.strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    return normalized


def get_provider_spec(provider_id: str) -> dict:
    if provider_id not in PROVIDER_REGISTRY:
        raise ValueError(f"unknown provider id: {provider_id}")
    spec = PROVIDER_REGISTRY[provider_id]
    return {
        "provider_id": str(spec.get("provider_id", "")).strip(),
        "provider_role": str(spec.get("provider_role", "")).strip(),
        "execution_mode": str(spec.get("execution_mode", "")).strip(),
        "supported_routes": _normalize_string_list(spec.get("supported_routes")),
        "capability_tags": _normalize_string_list(spec.get("capability_tags")),
        "preferred_object_types": _normalize_string_list(spec.get("preferred_object_types")),
        "discouraged_object_types": _normalize_string_list(spec.get("discouraged_object_types")),
        "expected_inputs": _normalize_string_list(spec.get("expected_inputs")),
        "expected_outputs": _normalize_string_list(spec.get("expected_outputs")),
        "expected_consume_mode": str(spec.get("expected_consume_mode", "")).strip(),
        "selection_notes": _normalize_string_list(spec.get("selection_notes")),
        "production_ready_requires": _normalize_string_list(spec.get("production_ready_requires")),
    }


def get_route_required_capability_tags(planned_route: str) -> list[str]:
    route = str(planned_route).strip()
    if route not in ROUTE_REQUIRED_CAPABILITY_TAGS:
        raise ValueError(f"unsupported planned route: {planned_route}")
    return list(ROUTE_REQUIRED_CAPABILITY_TAGS[route])


def get_default_route_chain(planned_route: str) -> list[str]:
    if planned_route not in DEFAULT_ROUTE_PROVIDER_CHAINS:
        raise ValueError(f"unsupported planned route: {planned_route}")
    return list(DEFAULT_ROUTE_PROVIDER_CHAINS[planned_route])


def get_object_type_override_chain(planned_route: str, object_type: str) -> list[str]:
    route = str(planned_route).strip()
    obj_type = str(object_type).strip()
    override = OBJECT_TYPE_PROVIDER_OVERRIDES.get((route, obj_type))
    if override is None:
        return []
    return list(override)


def get_default_provider_chain(planned_route: str, object_type: str) -> list[str]:
    override = get_object_type_override_chain(planned_route, object_type)
    if override:
        return override
    route = str(planned_route).strip()
    return get_default_route_chain(route)


def list_supported_provider_ids(planned_route: str) -> list[str]:
    route = str(planned_route).strip()
    provider_ids: list[str] = []
    for provider_id, spec in PROVIDER_REGISTRY.items():
        if provider_id not in V1_ACTIVE_PROVIDER_IDS:
            continue
        if route in spec["supported_routes"]:
            provider_ids.append(provider_id)
    return provider_ids


def describe_provider_capability_fit(planned_route: str, object_type: str, provider_id: str) -> dict:
    route = str(planned_route).strip()
    obj_type = str(object_type).strip()
    provider_spec = get_provider_spec(provider_id)
    route_required_capability_tags = get_route_required_capability_tags(route)
    provider_capability_tags = list(provider_spec["capability_tags"])
    missing_capability_tags = [
        item for item in route_required_capability_tags if item not in provider_capability_tags
    ]
    preferred_object_types = list(provider_spec["preferred_object_types"])
    discouraged_object_types = list(provider_spec["discouraged_object_types"])
    preferred_object_type_match = obj_type in preferred_object_types
    discouraged_object_type_match = obj_type in discouraged_object_types
    object_type_fit = "supported"
    if preferred_object_type_match:
        object_type_fit = "preferred"
    elif discouraged_object_type_match:
        object_type_fit = "discouraged"
    elif not obj_type:
        object_type_fit = "not-specified"
    notes = list(provider_spec["selection_notes"])
    if preferred_object_type_match:
        notes.append(f"Provider is explicitly preferred for object type {obj_type!r}.")
    elif discouraged_object_type_match:
        notes.append(f"Provider is not a preferred default for object type {obj_type!r}.")
    if missing_capability_tags:
        notes.append(
            "Provider does not advertise all route-required capability tags: "
            + ", ".join(missing_capability_tags)
        )
    else:
        notes.append("Provider covers the route-required capability tags for this object path.")
    return {
        "route_required_capability_tags": route_required_capability_tags,
        "provider_capability_tags": provider_capability_tags,
        "missing_capability_tags": missing_capability_tags,
        "preferred_object_types": preferred_object_types,
        "discouraged_object_types": discouraged_object_types,
        "preferred_object_type_match": preferred_object_type_match,
        "discouraged_object_type_match": discouraged_object_type_match,
        "object_type_fit": object_type_fit,
        "expected_consume_mode": str(provider_spec["expected_consume_mode"]),
        "selection_notes": notes,
    }
