# Historical Mock Pass

Use this reference when new image generation is not the right next move and the project already has usable visual material.

## When To Read It

Read when:

- the user says not to generate new images yet
- the repo already contains concept PNGs, screenshots, or archived visuals
- the goal is framework-first delivery
- existing project visuals are strong enough to guide route composition

## What Counts As Historical Mock Material

- approved concept boards
- route mockups from earlier phases
- exported screenshots from prior builds
- archived visual studies that still fit the chosen direction
- project-owned artwork, textures, or photos not yet fully integrated

## Workflow

1. Inventory the available visual files.
2. Classify each one with provenance status and source method.
3. Decide what each asset can control:
   - whole route composition
   - section composition
   - illustration slot shape
   - palette or texture only
4. Mark temporary route owners as `temporary-binding` when they are valid for the current pass but expected to be upgraded later.
5. Record limitations and upgrade triggers.
6. Use the assets as local mock inputs or direct binding references, depending on authority.

## Required Output

Record a compact note with:

- historical assets found
- authority status for each
- route or section ownership
- any `temporary-binding` usage
- what must later be upgraded

Use `assets/templates/mock-asset-pass.md` when the project lacks an equivalent document.

## Guardrails

- do not force `imagegen` when historical visual sources are already sufficient
- do not present provisional historical imagery as final bespoke artwork
- do not mix obsolete and binding references in one acceptance pass
- do not hotlink when a local project-owned file exists
- do not skip browser QA just because the asset is temporary
