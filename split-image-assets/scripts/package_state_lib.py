import json
from pathlib import Path

from semantic_scope_lib import ALLOWED_RESOURCE_FAMILIES, default_scope_selection


ASSET_SUMMARY_DEFAULT = {
    "production_ready_assets": 0,
    "accepted_approximate_reconstructions": 0,
    "accepted_generated_reconstructions": 0,
    "draft_candidate_assets": 0,
    "support_only_layers": 0,
    "blocked_assets": 0,
}


def summarize_asset_entries(entries: list[dict]) -> dict:
    summary = dict(ASSET_SUMMARY_DEFAULT)
    for item in entries:
        if not isinstance(item, dict):
            continue
        asset_class = item.get("asset_class")
        reuse_status = item.get("reuse_status")
        if asset_class == "atomic" and reuse_status == "production-ready":
            summary["production_ready_assets"] += 1
        elif reuse_status == "accepted-approximate-reconstruction":
            summary["accepted_approximate_reconstructions"] += 1
        elif reuse_status == "accepted-generated-reconstruction":
            summary["accepted_generated_reconstructions"] += 1
        elif reuse_status == "draft-candidate":
            summary["draft_candidate_assets"] += 1
        elif reuse_status in {"support-only", "approximate-reconstruction"} or asset_class in {
            "grouped-support",
            "background-support",
            "preview-reference",
        }:
            summary["support_only_layers"] += 1
        elif reuse_status == "blocked":
            summary["blocked_assets"] += 1
    return summary


def update_asset_summary(metadata: dict) -> None:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        metadata["asset_summary"] = dict(ASSET_SUMMARY_DEFAULT)
        return
    metadata["asset_summary"] = summarize_asset_entries(objects)


def plan_manifest_path(package_dir: Path) -> Path:
    return package_dir / "plan_manifest.json"


def normalize_scope_selection(scope_selection: dict | None) -> dict:
    normalized = default_scope_selection()
    if not isinstance(scope_selection, dict):
        return normalized
    for key in normalized:
        value = scope_selection.get(key, normalized[key])
        if key == "candidate_families":
            if not isinstance(value, list):
                value = []
            deduped: list[str] = []
            for item in value:
                family = str(item).strip()
                if family and family in ALLOWED_RESOURCE_FAMILIES and family not in deduped:
                    deduped.append(family)
            value = deduped
        else:
            value = str(value or "").strip()
            if key == "selection_source" and not value:
                value = normalized[key]
        normalized[key] = value
    return normalized


def normalize_plan_manifest(plan_manifest: dict) -> dict:
    normalized = dict(plan_manifest)
    normalized["scope_selection"] = normalize_scope_selection(plan_manifest.get("scope_selection"))
    return normalized


def read_plan_manifest(package_dir: Path) -> dict | None:
    path = plan_manifest_path(package_dir)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("plan_manifest.json must contain an object")
    return normalize_plan_manifest(data)


def write_plan_manifest(package_dir: Path, data: dict) -> None:
    plan_manifest_path(package_dir).write_text(
        json.dumps(normalize_plan_manifest(data), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def find_plan_object(plan_manifest: dict | None, object_id: str) -> dict | None:
    if not isinstance(plan_manifest, dict):
        return None
    objects = plan_manifest.get("objects", [])
    if not isinstance(objects, list):
        return None
    for item in objects:
        if isinstance(item, dict) and item.get("object_id") == object_id:
            return item
    return None
