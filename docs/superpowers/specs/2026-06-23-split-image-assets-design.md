# Split Image Assets Skill Design

## Goal

Create `split-image-assets` as the sixth public skill in this repository. The skill turns a source image into a reusable asset package with independent transparent PNG layers, masks, cleaned background, metadata, previews, and QA evidence.

The skill is a production workflow, not a one-shot prompt. Its highest-value output is a managed asset package that can be reused in UI, layout, animation, compositing, and later manual editing. A 2x2 sprite sheet is only a preview artifact.

## Recommended Approach

Use a semi-automatic image-processing skill:

- Codex guides analysis, object inventory, risk classification, and asset-package decisions.
- Users, AI image tools, or external segmentation tools may produce actual cutouts, masks, and background repairs.
- Bundled Python scripts provide deterministic package initialization, preview generation, and structural validation.

This avoids pretending that deterministic scripts can solve every segmentation case while still making the final package reliable and inspectable.

## Skill Package Layout

```text
split-image-assets/
  SKILL.md
  agents/
    openai.yaml
  references/
    workflow.md
    asset-package-contract.md
    qa-standards.md
    manual-review.md
  scripts/
    init_asset_package.py
    build_previews.py
    validate_asset_package.py
  tests/
    test_skill_package.py
docs/usage/split-image-assets.md
```

Repository navigation must also be updated so README, skill matrix, release docs, Chinese overview, and repository docs tests treat it as a first-class sixth skill.

## Core Workflow

1. Intake source image and create or identify an output package directory.
2. Run package initialization to create the expected folder layout and starter `metadata.json` plus `qa_report.md`.
3. Analyze the image before extraction:
   - source dimensions
   - main object
   - secondary objects
   - background type
   - occlusion
   - complex edge regions
   - transparent, reflective, smoky, fuzzy, or soft-edge areas
   - expected segmentation difficulty
4. Write an object inventory and recommended split plan into metadata.
5. Produce or collect asset files:
   - source backup
   - transparent PNG for each reusable object
   - mask PNG for each object
   - `background_clean.png`
   - optional shadow layer
   - optional grouped secondary object layer
6. Build inspection previews:
   - white-background previews
   - checkerboard previews
   - overview layout
   - 2x2 sprite sheet
7. Validate package structure and basic image properties.
8. Write QA status as `pass`, `needs-review`, or `blocked`.
9. Report exact outputs, risks, and manual-review items to the user.

## Asset Package Contract

The default output package should use this shape:

```text
asset-package/
  source/
    source_original.png
  assets/
    main_object_transparent.png
    secondary_01_transparent.png
    secondary_group.png
    shadow_optional.png
    background_clean.png
  masks/
    mask_main.png
    mask_secondary_01.png
    mask_all_foreground.png
  previews/
    main_object_whitebg.png
    main_object_checkerboard.png
    overview_decomposition.png
    sprite_sheet_2x2.png
  metadata.json
  qa_report.md
```

The contract must allow object counts to vary. The naming convention should prefer `main_object`, then `secondary_01`, `secondary_02`, and so on. `metadata.json` records the complete inventory so the file list is not hard-coded to one fixed object count.

## Metadata Contract

`metadata.json` should include:

- package schema version
- source image path and dimensions
- object inventory
- role for each object: `main`, `secondary`, `group`, `background`, `shadow`
- bounding box in source coordinates when known
- width, height, aspect ratio, and area ratio when known
- extraction method: `exact`, `ai-assisted`, `manual`, `estimated`, or `unknown`
- confidence: `high`, `medium`, or `low`
- edge complexity level: `hard`, `soft`, or `transparent-reflective`
- generated/inpainted regions
- manual review flags
- final QA status

## Script Responsibilities

### `init_asset_package.py`

Create the standard directory structure, copy the source image into `source/source_original.png`, and write starter `metadata.json` and `qa_report.md`.

Inputs:

- source image path
- output package directory
- optional package name

### `build_previews.py`

Use Pillow to build deterministic preview images from existing transparent PNGs:

- white-background preview
- checkerboard preview
- overview layout
- 2x2 sprite sheet

The script must not claim to perform segmentation. It only composites already-produced assets for inspection.

### `validate_asset_package.py`

Validate:

- required files exist
- `metadata.json` is parseable and contains required top-level fields
- referenced assets exist
- transparent object PNGs have alpha channels
- masks are image files and match the source image size when they are source-space masks
- previews exist after preview generation
- QA report contains a final status
- manual-review flags are present when metadata has low-confidence or AI-assisted work

The validator should return nonzero for structural failures and print actionable messages.

## QA Standards

QA must cover:

- Structure: required files and metadata exist.
- Proportion: objects keep original aspect ratio and relative size where known.
- Edge quality: no obvious halos, colored fringes, jagged edges, or background residue.
- Background repair: no obvious ghosts, repeated texture artifacts, broken perspective, or lighting discontinuity.
- Reuse readiness: transparent assets can be dropped onto new backgrounds, and previews are clearly marked as inspection artifacts.
- Provenance: exact extraction, AI-assisted generation, background repair, uncertainty, and manual-review areas are explicitly labeled.

The skill should never hide uncertainty. Complex transparent, reflective, fuzzy, smoky, occluded, or low-contrast regions should become `needs-review` unless fresh evidence supports a pass.

## Manual Review Branch

Enter manual review when:

- segmentation confidence is low
- main and background colors are too similar
- objects overlap heavily
- reflective or transparent materials dominate the object
- background inpainting looks unnatural
- object count or role assignment is uncertain
- mask preview reveals edge contamination

Manual review output should include the preliminary package, previews, issue list, and recommended correction areas.

## Documentation Updates

Add `docs/usage/split-image-assets.md` with:

- what the skill is for
- when to use it
- expected workflow
- command examples
- output package shape
- QA interpretation
- limitations around automatic segmentation

Update repository docs to list six skills and route readers to the new usage page.

## Tests

Add package tests that verify:

- `SKILL.md` frontmatter is valid
- required references and scripts exist
- scripts have help text or runnable CLI entrypoints
- usage docs mention the package contract, previews, metadata, QA, and manual review
- repository docs list `split-image-assets`

Add script-level tests with a generated tiny RGBA fixture to verify preview generation and validator behavior without needing external image models.

## Acceptance Criteria

- The new skill validates with `skill-creator` quick validation.
- The new package tests pass.
- Repository docs tests pass.
- `init_asset_package.py`, `build_previews.py`, and `validate_asset_package.py` run successfully on a tiny local fixture.
- README and usage navigation present the repository as a six-skill collection.
- The skill clearly distinguishes reusable assets from preview-only outputs.
- The skill clearly distinguishes deterministic script behavior from AI/manual image extraction work.

