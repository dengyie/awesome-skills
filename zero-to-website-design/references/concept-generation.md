# Concept Generation

Use this reference when the project lacks enough repo-owned, historical, user-provided, or temporary visual authority to proceed, or when the user explicitly asks to generate design images before implementation.

Do not treat generation as the default first move. Inspect existing project visuals first.

## Concept Flow

1. Generate or collect 3-4 distinct directions.
2. Make each direction materially different in layout, visual language, density, and mood.
3. Show or name the tradeoffs clearly.
4. Ask the user to choose or combine directions.
5. Extend the selected direction into route-specific mockups.
6. Record selected images in the visual source map.

## Image Generation Guidance

Use image generation for:

- visual direction boards
- homepage mockups
- route mockups
- asset panels, illustrations, textures, icons, or decorative systems

Prompt for:

- actual website screenshot or mockup, not abstract mood art
- desktop and mobile frames when responsive fidelity matters
- route-specific UI states
- realistic text scale and navigational structure
- the intended site type and audience
- visual motifs that can be implemented with CSS, SVG, or local images

Prefer historical or repo-owned visual sources when:

- the project already has approved concept work
- a framework-first pass is enough for the current stage
- new generation is constrained, unnecessary, or undesired

Avoid:

- vague "modern website" prompts
- one-note color palettes
- decorative visuals that cannot become a usable UI
- mockups with unreadable microtext as the only source of truth
- relying on generated images for factual content accuracy

## Concept Status Rules

Generated images start as `exploratory`.

Move an image to `candidate` when it is good enough for user selection.

Move it to `approved-direction` only when the user chooses it.

Move it to `binding-route` only when it controls implementation for a route or section.

Move it to `temporary-binding` when it is valid for the current framework or mock-asset pass but expected to be upgraded later.

If a later design replaces it, mark the old image `obsolete` instead of deleting history.

## Route Mockup Expansion

After the user chooses a concept, generate or define mockups for the routes that carry the design system:

- homepage
- listing/index page
- detail/content page
- category/filter/archive page when relevant
- one mobile frame for the hardest layout

Implementation should begin only after the route ownership is clear.
