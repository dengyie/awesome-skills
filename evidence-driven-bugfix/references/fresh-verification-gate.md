# Fresh Verification Gate

## Purpose

Prove that the original failure has actually been removed.

## Required Inputs

You must:

- rerun or recheck the same failing evidence chain
- verify the original failure has turned green or disappeared as expected
- run the minimum necessary regression checks
- read the actual output

## Prohibited Shortcuts

Do not:

- rely on stale results
- rely on partial checks
- infer success from code plausibility
- claim success from a linter or unrelated command

## Pass Condition

Fresh evidence proves the original failing signal is now passing or absent, and required regressions do not introduce a new blocker.
