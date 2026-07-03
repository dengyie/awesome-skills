import argparse
import sys
from pathlib import Path

from split_image_assets_contract import (
    ALLOWED_ASSET_CLASSES,
    ALLOWED_BLOCKING_VALUES,
    ALLOWED_CAPABILITY_CHOICES,
    ALLOWED_CARRIER_GLYPH_POLICIES,
    ALLOWED_CONFIRMATION_SOURCES,
    ALLOWED_CONFIRMATION_STATUSES,
    ALLOWED_DECISION_SOURCES,
    ALLOWED_DELIVERY_CLASSES,
    ALLOWED_GENERATION_PROVIDER_CLASSES,
    ALLOWED_GRANULARITY_MODES,
    ALLOWED_LAYER_INDEPENDENCE,
    ALLOWED_OBJECT_TYPES,
    ALLOWED_PAUSE_CATEGORIES,
    ALLOWED_QA_STATUSES,
    ALLOWED_QUALITY_CHECK_STATUSES,
    ALLOWED_QUALITY_TARGET_TIERS,
    ALLOWED_REUSE_STATUSES,
    ALLOWED_ROUTING_ACTIONS,
    ALLOWED_ROUTING_DECISION_SOURCES,
    ALLOWED_SCORE_VALUES,
    ALLOWED_SCOPE_STRATEGIES,
    ALLOWED_TEXT_HANDLING,
    ALLOWED_TEXT_RENDER_CLASSES,
    ALLOWED_TEXT_ROLES,
    ALLOWED_BACKGROUND_EXPECTATIONS,
    NON_DEFAULT_CONFIRMATION_SOURCES,
    ORDINARY_TEXT_ROLES,
    REQUIRED_CONFIRMATION_KEYS,
)
from validator_metadata_lib import validate_extraction_pipeline, validate_metadata_fields
from validator_objects_lib import validate_objects
from validator_package_artifacts_lib import (
    validate_previews,
    validate_qa_report,
    validate_required_layout,
    validate_source,
)
from validator_shared import (
    ALLOWED_AUDIT_CODES,
    AFFIRMATIVE_DECISION_ANSWERS,
    APPROXIMATE_RECONSTRUCTION_ACCEPTANCE_STAGES,
    CROP_ONLY_MARKERS,
    DECISION_ANSWER_FIELDS,
    GENERATED_EVIDENCE_FIELDS,
    HELPER_ONLY_MARKERS,
    OBJECT_ASSET_ROLES,
    PASS_READY_REUSE_STATUSES,
    RECONSTRUCTION_MARKERS,
    REQUIRED_ASSET_SUMMARY_FIELDS,
    REQUIRED_CANDIDATE_COMPARISON_FIELDS,
    REQUIRED_DECISION_FIELDS,
    REQUIRED_NONEMPTY_DECISION_FIELDS,
    REQUIRED_OBJECT_QUALITY_CHECKS,
    REQUIRED_PIPELINE_STAGES,
    TEXT_ROUTING_CONFIRMATION_MARKERS,
    TEXT_ROUTING_CONFIRMATION_STAGES,
    confirmation_satisfies_promotion,
    decision_answer,
    find_plan_object,
    has_affirmative_decision,
    has_alpha,
    has_carrier_layer,
    has_glyph_layer,
    has_text_routing_confirmation,
    image_mode,
    image_size,
    is_affirmative_answer,
    is_crop_only_layer,
    is_generated_delivery_layer,
    is_helper_only_layer,
    is_placeholder_only_rebuild,
    is_reconstructed_or_approximate_layer,
    is_ui_like_package,
    iter_preview_paths,
    load_metadata,
    load_plan_manifest,
    promotion_confirmation_satisfied,
    rel_path,
    require_preview_path,
    requires_candidate_comparison_evidence,
    requires_object_type,
)


def collect_validation_errors(package_dir: Path, metadata: dict | None = None) -> list[str]:
    errors: list[str] = []
    if not package_dir.is_dir():
        errors.append(f"package directory does not exist: {package_dir}")
        return errors

    candidate_metadata = metadata if isinstance(metadata, dict) else load_metadata(package_dir, errors)
    plan_manifest = load_plan_manifest(package_dir, errors)
    validate_required_layout(package_dir, errors)
    validate_metadata_fields(candidate_metadata, errors)
    validate_extraction_pipeline(candidate_metadata, errors)
    source_size = validate_source(package_dir, candidate_metadata, errors)
    validate_objects(package_dir, candidate_metadata, source_size, errors, plan_manifest=plan_manifest)
    validate_previews(package_dir, candidate_metadata, errors)
    validate_qa_report(package_dir, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a split image asset package.")
    parser.add_argument("package_dir", help="Asset package directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    errors = collect_validation_errors(package_dir)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Package valid: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
