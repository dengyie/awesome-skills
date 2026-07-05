ALLOWED_RESOURCE_FAMILIES = {
    "blueprint-modules",
    "paper-scraps",
    "right-rail-hardware",
    "hero-ornaments",
    "component-panels",
    "other",
}

WEAK_AUTONOMY_EVIDENCE_MARKERS = (
    "continue",
    "default option",
    "use your default",
    "you decide",
    "do not stop unless needed",
    "project recommends narrow package",
)


def default_scope_selection() -> dict:
    return {
        "candidate_families": [],
        "selected_family": "",
        "selection_source": "unresolved",
        "selection_evidence_ref": "",
        "selection_notes": "",
    }


def is_weak_autonomy_evidence(evidence_ref: str) -> bool:
    normalized = str(evidence_ref or "").strip().lower()
    return any(marker in normalized for marker in WEAK_AUTONOMY_EVIDENCE_MARKERS)
