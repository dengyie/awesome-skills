# Concept Generation

Use this reference when the project lacks binding visual sources or when the user asks to generate design images before implementation.

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

Avoid:

- vague "modern website" prompts
- one-note color palettes
- decorative visuals that cannot become a usable UI
- mockups with unreadable microtext as the only source of truth
- relying on generated images for factual content accuracy

## Concept Status Rules

Generated images start as `exploratory`.

Move an image to `candidate` when it is good enough for user selection.

Move it to `approved` only when the user chooses it.

Move it to `binding` only when it controls implementation for a route or section.

If a later design replaces it, mark the old image `obsolete` instead of deleting history.

## Route Mockup Expansion

After the user chooses a concept, generate or define mockups for the routes that carry the design system:

- homepage
- listing/index page
- detail/content page
- category/filter/archive page when relevant
- one mobile frame for the hardest layout

Implementation should begin only after the route ownership is clear.

