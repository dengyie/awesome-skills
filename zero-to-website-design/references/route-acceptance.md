# Route Acceptance

Use this reference before implementing or reviewing routes.

## Route Evidence Contract

Every touched core route needs a compact evidence row before final handoff.

Use this format in the project QA report or equivalent delivery note:

```md
| Route | Route Type | Source Owner | Viewports Checked | Evidence | Item Audit | Status | Blocking Failures | Accepted Gaps | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/posts` | listing | `binding-route`: output/design/posts.png | 1600x900, 390x844 | output/qa/posts-1600x900.png; output/qa/posts-390x844.png | output/qa/posts-item-audit.md | framework-ready | none | final art remains temporary | Mobile menu and links verified |
```

Allowed route evidence statuses:

- `not-checked`: route exists but lacks browser evidence
- `blocked`: route was checked and has failures that prevent the claimed milestone
- `framework-ready`: route satisfies Level A with recorded evidence
- `visual-delivery-ready`: route satisfies Level A and Level B with recorded evidence

Do not claim a route status that is stronger than its evidence row supports.

## Level A: Framework Ready

- Route has a clear purpose.
- Header/navigation works.
- Footer or end state is present when appropriate.
- Desktop layout matches the intended composition.
- Mobile layout is intentional, not accidental stacking.
- Text does not overlap or overflow.
- Images and local assets load.
- Links and primary actions are clickable.
- Placeholder or `temporary-binding` assets are correctly placed.
- Temporary-binding assets have documented route ownership and replacement triggers.
- Metadata is coherent enough for the current framework pass.
- No rejected placeholder brand remains.
- Route works in the target build/export mode.
- Route composition is accepted even if final imagery is still provisional.

Failed layout, link, asset-loading, console-blocking, or page-level overflow checks block `Framework Ready` unless the route is explicitly out of scope.

## Level B: Visual Delivery Ready

- Route satisfies all `Framework Ready` expectations.
- Every binding design item for the route and required viewport is audited as `matched` or `accepted-gap`.
- Visual hierarchy is tuned against the binding reference.
- Asset quality is acceptable for delivery.
- Metadata is correct.
- Temporary-binding assets are either upgraded or explicitly acknowledged as remaining gaps with their remaining scope clearly stated.

Unresolved fidelity gaps, unchecked design items, blocked item-level mismatches, incorrect metadata, weak asset quality, or unacknowledged `temporary-binding` ownership block `Visual Delivery Ready`.

## Failure Handling

Classify each failed check as:

- `blocking-framework`: prevents `Framework Ready`
- `blocking-visual`: allows `Framework Ready` but prevents `Visual Delivery Ready`
- `accepted-gap`: explicitly allowed for this milestone and documented with scope
- `out-of-scope`: not part of the route matrix for this pass

Accepted gaps must name the route, viewport, reason, remaining owner, and what would close the gap.

## Homepage

- first viewport clearly signals the brand or offer
- primary navigation is visible or accessible
- key content modules are visible without needing explanatory in-app text
- visual system appears immediately
- next section is hinted on typical desktop and mobile screens

## Listing Or Index Page

- items are scannable
- card rhythm matches the design direction
- filters/categories/search controls are usable when present
- empty and low-count states do not break layout
- pagination or load-more behavior is clear when present

## Detail Or Content Page

- title, metadata, and body hierarchy are clear
- long text remains readable
- code, tables, images, lists, and quotes are styled if content can contain them
- related/navigation links do not trap the user
- mobile line length and overflow are checked

## Category, Filter, Or Archive Page

- current category/filter is obvious
- item count or scope is clear when useful
- category navigation remains available
- low-count categories still produce a balanced layout
- generated/static paths match actual data

## Landing Or Product Page

- primary value is visible in the first viewport
- call to action is clear
- feature sections support the claim
- pricing, proof, or next-step content is reachable when relevant
- no ornamental layout blocks the conversion path

## Documentation Page

- navigation and current location are clear
- headings create a usable scan path
- code blocks and examples are readable
- search or table of contents exists when content volume needs it
- mobile docs navigation is usable
