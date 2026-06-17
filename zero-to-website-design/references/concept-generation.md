# Concept Generation

Use this reference when the project lacks enough repo-owned, historical, user-provided, or temporary visual authority to proceed, or when the user explicitly asks to generate design images before implementation.

Do not treat generation as the default first move. Inspect existing project visuals first.

## Generation Entry Conditions

Start a generation pass only when at least one of these is true:

- the user explicitly asks to generate concept images or route mockups
- the project lacks enough repo-owned, historical, or user-provided visuals to continue
- the current milestone needs a route owner that existing visuals cannot supply
- the current visuals are too weak, too incomplete, or too conflicting to support the intended route

Before generation, record why the stronger non-generated source paths were not sufficient for this pass.

## Concept Flow

1. Generate or collect 3-4 distinct directions.
2. Make each direction materially different in layout, visual language, density, and mood.
3. Show or name the tradeoffs clearly.
4. Ask the user to choose or combine directions.
5. Extend the selected direction into route-specific mockups.
6. Record selected images in the visual source map.
7. Record whether the generated outputs are only for direction, `temporary-binding`, or intended to become `binding-route` later.

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

When generation is still chosen, record:

- why generation was necessary
- which source path was considered first
- what route or section the new image is expected to control
- what stronger source would later replace it, if any

Avoid:

- vague "modern website" prompts
- one-note color palettes
- decorative visuals that cannot become a usable UI
- mockups with unreadable microtext as the only source of truth
- relying on generated images for factual content accuracy

## Concept Status Rules

Generated images start as `exploratory`.

Move an image to `candidate` when it is good enough for user selection.

Only move it to `candidate` after the generated image is:

- materially distinct from the other directions
- legible enough to support real route discussion
- specific enough to the actual website type and audience

Move it to `approved-direction` only when the user chooses it.

Only move it to `approved-direction` when the chosen image is also recorded with:

- route family or system scope
- viewport coverage or known gap
- known limitations that matter for implementation

Move it to `binding-route` only when it controls implementation for a route or section.

Only move it to `binding-route` when all of these are true:

- route ownership is explicit
- milestone supported is explicit
- replacement trigger is explicit
- the image is specific enough to guide implementation without relying on private guesswork

Move it to `temporary-binding` when it is valid for the current framework or mock-asset pass but expected to be upgraded later.

Only move it to `temporary-binding` when:

- the generated image is strong enough for the current milestone
- the expected upgrade path is known
- final delivery does not pretend the generated output is already the final source of truth

If a later design replaces it, mark the old image `obsolete` instead of deleting history.

When a generated image is retired, record what replaced it:

- approved historical or repo-owned source
- newer generated mockup
- final route-specific manual design

## Route Mockup Expansion

After the user chooses a concept, generate or define mockups for the routes that carry the design system:

- homepage
- listing/index page
- detail/content page
- category/filter/archive page when relevant
- one mobile frame for the hardest layout

Implementation should begin only after the route ownership is clear.

## Guardrails

- do not generate merely because generation is available
- do not let a generated direction silently become route-binding
- do not skip recording why generation beat repo-owned or historical sources
- do not treat decorative image output as enough authority for route implementation
