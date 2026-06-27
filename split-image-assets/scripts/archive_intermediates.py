import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def collect_staging_entries(staging_dir: Path) -> list[Path]:
    return sorted(staging_dir.iterdir(), key=lambda path: path.name)


def move_entry(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def read_metadata(package_dir: Path) -> dict | None:
    metadata_path = package_dir / "metadata.json"
    if not metadata_path.exists():
        return None
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_archived_metadata(package_dir: Path, moved_paths: dict[str, str]) -> None:
    metadata = read_metadata(package_dir)
    if not isinstance(metadata, dict):
        return
    audit = metadata.get("audit")
    if isinstance(audit, dict):
        quality_path = audit.get("quality_audit_path")
        if isinstance(quality_path, str) and quality_path in moved_paths:
            audit["quality_audit_path"] = moved_paths[quality_path]
    previews = metadata.get("previews")
    if isinstance(previews, dict):
        audit_preview = previews.get("qa_audit_contact_sheet")
        if isinstance(audit_preview, str) and audit_preview in moved_paths:
            previews["qa_audit_contact_sheet"] = moved_paths[audit_preview]
    objects = metadata.get("objects")
    if isinstance(objects, list):
        for item in objects:
            if not isinstance(item, dict):
                continue
            candidate_comparisons = item.get("candidate_comparisons")
            if not isinstance(candidate_comparisons, list):
                continue
            for comparison in candidate_comparisons:
                if not isinstance(comparison, dict):
                    continue
                compare_artifact_path = comparison.get("compare_artifact_path")
                if isinstance(compare_artifact_path, str) and compare_artifact_path in moved_paths:
                    comparison["compare_artifact_path"] = moved_paths[compare_artifact_path]
                compare_manifest_path = comparison.get("compare_manifest_path")
                if isinstance(compare_manifest_path, str) and compare_manifest_path in moved_paths:
                    comparison["compare_manifest_path"] = moved_paths[compare_manifest_path]
                score_manifest_path = comparison.get("score_manifest_path")
                if isinstance(score_manifest_path, str) and score_manifest_path in moved_paths:
                    comparison["score_manifest_path"] = moved_paths[score_manifest_path]
    write_metadata(package_dir, metadata)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Archive active intermediate extraction outputs from _staging into _archive_intermediate."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--run-id", required=True, help="Archive bucket name, such as a run id or timestamp label.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    staging_dir = package_dir / "_staging"
    archive_dir = package_dir / "_archive_intermediate" / args.run_id
    if not staging_dir.is_dir():
        parser.error(f"_staging directory is missing: {staging_dir}")
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived_paths: list[str] = []
    moved_paths: dict[str, str] = {}
    for entry in collect_staging_entries(staging_dir):
        old_root_rel = str(entry.relative_to(package_dir)).replace("\\", "/")
        destination = archive_dir / entry.name
        move_entry(entry, destination)
        if destination.is_dir():
            for child in sorted(destination.rglob("*")):
                if child.is_file():
                    archived_paths.append(str(child.relative_to(archive_dir)).replace("\\", "/"))
                    new_rel = str(child.relative_to(package_dir)).replace("\\", "/")
                    old_rel = str(Path(old_root_rel) / child.relative_to(destination)).replace("\\", "/")
                    moved_paths[old_rel] = new_rel
        else:
            archived_paths.append(destination.name)
            moved_paths[old_root_rel] = str(destination.relative_to(package_dir)).replace("\\", "/")

    update_archived_metadata(package_dir, moved_paths)

    manifest = {
        "run_id": args.run_id,
        "archived_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archived_paths": archived_paths,
    }
    (archive_dir / "archive_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Archived intermediates to: {archive_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
