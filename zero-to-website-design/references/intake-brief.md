# Intake Brief

Use this reference when the user starts with a vague website idea, a partial brand, or no clear site structure.

## Minimum Useful Intake

Collect or infer:

- site type: blog, portfolio, product site, landing page, docs, app shell, marketing site, community site
- primary audience
- primary action or reading path
- brand/product/person name
- tone: calm, technical, playful, editorial, premium, practical, experimental, other
- content readiness: real content, placeholder content, generated draft content, existing CMS/content files
- visual references: user-provided, generated, live sites, Figma, screenshots, none yet
- delivery target: static export, Vercel, GitHub Pages, existing app, local prototype
- hard constraints: framework, design system, accessibility, performance, SEO, deadline

Ask at most three questions before starting. If the answer can be reasonably assumed, proceed and record the assumption in the project docs.

## Default Assumptions

When the user does not specify:

- build the actual usable site, not a marketing explanation of the site
- prioritize homepage plus the minimum route set needed for the site type
- use responsive desktop and mobile layouts
- create project-owned assets or CSS/SVG primitives instead of hotlinked images
- document visual decisions before code
- keep content realistic enough to test layout, but do not over-invest in copy unless requested

## Site Type Route Seeds

Blog:

- `/`
- `/posts`
- `/posts/[slug]`
- `/categories/[category]`

Portfolio:

- `/`
- `/work`
- `/work/[slug]`
- `/about`

Product or landing site:

- `/`
- `/pricing` when relevant
- `/docs` or `/guide` when the product needs explanation
- `/contact` or primary conversion route

Documentation site:

- `/`
- `/docs`
- `/docs/[slug]`
- search or category routes when content volume requires it

## Intake Output

Before concept generation or implementation, write a compact brief:

- objective
- audience
- route inventory
- visual direction inputs
- content and asset strategy
- delivery target
- assumptions
- open decisions

