# FAQ

## Why does this skill collect repo context before reviewing?

Because review quality depends heavily on scope. Without deterministic context, Codex is more likely to:

- report unrelated worktree files
- misclassify pre-existing issues
- overstate findings without changed-line evidence

## When should I use `collect-review-context.py`?

Use it whenever you want machine-readable review scope or when another tool needs structured data.

## When should I use `review-entrypoint.py`?

Use it when you want a quick human-readable review brief before asking Codex for a full review.

## Why are there fewer reference files now?

The skill was intentionally simplified for maintainability. The current references keep the highest-value splits while reducing browse cost and routing overhead.

## Why does the skill still include smaller helper scripts?

Because they are useful building blocks for narrow automation, even if most users only need:

- `collect-review-context.py`
- `review-entrypoint.py`

The default deterministic entrypoint is `collect-review-context.py`. The smaller scripts are mostly for subset automation, debugging, or integration glue.

## What is `.skill-source-dir`?

It is a small metadata file written into the installed skill copy.

Its only job is to remember which repo checkout the install came from, so `update-local-skill.sh` can refresh safely from that source later.

Treat it as part of the local install contract, not as a cache file to clean up.

## Does this skill replace human code review?

No. It is designed to improve review quality and reduce false positives, not replace judgment. The strongest use case is as a production-minded assistant before or during human review.

## What does “specialist review lenses” mean now that there are fewer prompt files?

It means the skill can still reason about a change through several perspectives:

- correctness
- architecture
- reliability
- security
- tests

The structure is lighter, but the review posture is still there.
