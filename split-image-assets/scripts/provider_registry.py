V1_ACTIVE_PROVIDER_IDS = {
    "external-professional-outputs",
    "external-generated-outputs",
    "codex-controlled-generation",
    "grounded-sam-bridge",
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
        "expected_inputs": ["source_image", "source_crop", "rough_mask", "bbox"],
        "expected_outputs": ["asset_png", "source_space_mask"],
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
        "expected_inputs": ["provider_manifest"],
        "expected_outputs": ["provider_manifest"],
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
        "expected_inputs": ["generation_brief", "reference_inputs"],
        "expected_outputs": ["candidate_png", "compare_ready_candidate"],
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
        "expected_inputs": ["generation_brief", "reference_inputs"],
        "expected_outputs": ["candidate_png", "compare_ready_candidate"],
        "production_ready_requires": [
            "transparent generated asset delivery",
            "compare and promotion evidence",
        ],
    },
}


def get_provider_spec(provider_id: str) -> dict:
    if provider_id not in PROVIDER_REGISTRY:
        raise ValueError(f"unknown provider id: {provider_id}")
    return PROVIDER_REGISTRY[provider_id]


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
