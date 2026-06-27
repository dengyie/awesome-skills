# Confirmation Prompts

Use these prompts when a split decision affects reuse boundaries, editability, animation readiness, localization, approximate reconstruction acceptance, or final delivery claims.

Ask one question at a time. Include the recommended answer. Resolve that branch before moving on. If the source image, metadata, or prior user instructions already answer the question, record the decision instead of asking again.

These prompts are workflow gates, not optional suggestions. Record each gate with a confirmation source:

- `explicit-user-confirmed`
- `inferred-from-user`
- `agent-defaulted`

## Tooling Preflight Confirmation

Question: Production-quality asset splitting needs professional upstream tools. This environment is missing [missing capabilities/tools]. Should I pause so you can install/activate them, use external segmented assets/masks, or continue as draft-packaging-only?

Recommended answer: For production-quality extraction, install or provide SAM2/Grounded-SAM plus rembg/BiRefNet/RMBG-style matting. Continue draft-packaging-only only when a reviewable package is enough and `qa.status` can remain `needs-review`.

Decision effect: Record the choice in `metadata.capability` and `metadata.decision_log[]`, set capability status to `production-capable` or `draft-packaging-only`, and do not claim production extraction when the user chooses draft-only.

## Granularity Confirmation

Question: Should this package target module, component, atomic-layer, or production-editable reconstruction granularity?

Recommended answer: Use `atomic-layer` for UI assets when reuse, animation, or clean icon separation matters; use `component` only for quick draft review.

Decision effect: Record `metadata.granularity.mode`, `metadata.granularity.user_confirmed`, `metadata.granularity.notes`, and a `metadata.decision_log` entry.

## Pilot Object Gate

Question: Before I continue with the broader batch, should I use this representative object as a pilot and wait for your confirmation on granularity and cleanliness?

Recommended answer: Yes for complex UI, dashboard, badge/tile/glyph, or approximate reconstruction work.

Decision effect: Record `metadata.confirmation.pilot_object` with the chosen object id and stop wider batch extraction until it is `confirmed` or explicitly `not-required`.

## Carrier And Glyph Split

Question: Should this icon or badge be split into a carrier tile and foreground glyph?

Recommended answer: Yes, when the carrier shape and glyph have different reuse, recolor, animation, or cleanup needs.

Decision effect: Create separate carrier and glyph object records, masks, previews, and quality checks.

## Text Or UI Chrome

Question: Should text, labels, buttons, or UI chrome be extracted as image layers or rebuilt downstream as live UI/text?

Recommended answer: Rebuild text and labels downstream when localization, editing, or crisp rendering matters.

Decision effect: Record whether text is excluded from image assets, extracted as image layers, or represented as grouped reference layers.

## Approximate Background Acceptance

Question: Is an approximate reconstructed background or support plate acceptable for this package?

Recommended answer: Accept approximate support plates only as `needs-review` unless the user explicitly accepts them for the target use.

Decision effect: Record `approximate: true`, `reconstruction_provenance`, quality checks, and any manual confirmation.

## Low-Confidence Mask Handling

Question: Should this low-confidence mask be retried with another upstream tool, sent to manual review, or retained as draft-only evidence?

Recommended answer: Retry with a stronger upstream tool when the object is central; send to manual review when the boundary is subjective; retain draft-only for non-critical evidence.

Decision effect: Keep `qa.status` as `needs-review` or `blocked` until the selected path is complete.

## Final User Acceptance

Question: Does the current package meet the requested granularity and cleanliness well enough to mark `qa.status=pass`?

Recommended answer: Keep `needs-review` unless the user has explicitly accepted the current layer boundaries, cleanliness, and reconstructed regions.

Decision effect: Only promote to `pass` after required quality checks pass and the acceptance decision is recorded.
