# Production Code Quality Review V19 Install Path Guard Plan

## Milestone

Harden the `production-code-quality-review` local install and update helpers against destructive target-path mistakes.

## Problem

`install-local-skill.sh` and `update-local-skill.sh` intentionally clean the installed skill directory before copying fresh content. The clean-copy behavior keeps generated cache files out of the installed package, but the delete step currently trusts environment-derived paths.

If `AGENTS_HOME`, `SKILL_INSTALL_DIR`, `CODEX_HOME`, or the installed `.skill-source-dir` metadata points at an unexpected location, the script can remove the wrong directory before the copy step fails.

## P0/P1 Scope

- Add a shared shell guard before every destructive target cleanup.
- Reject empty, root-like, home-like, skill-root, source-equal, and source-nested target paths.
- Preserve the existing happy path for default installs and legacy copy sync.
- Add regression coverage for the guard contract.

## Out Of Scope

- Replacing the shell installers with Python.
- Changing the install destination defaults.
- Broad release documentation rewrites.
- Extending the same pattern to unrelated skill packages in this milestone.

## Design

The scripts keep their current clean-copy structure, but `copy_skill_tree` must call a `guard_skill_target` helper before `rm -rf`.

The guard resolves paths with `pwd -P` so symlinked parents are compared consistently when available. It then enforces:

- the target basename must be `production-code-quality-review`
- the target path must not be `/`
- the target path must not be `$HOME`, `$HOME/.agents`, `$HOME/.agents/skills`, `$HOME/.codex`, or `$HOME/.codex/skills`
- source and target must not resolve to the same directory
- source and target must not be nested inside each other

The nesting rule prevents deleting either a target accidentally created under the source checkout or a target parent that contains the recorded source checkout.

## Verification

- Static regression tests for guard presence and destructive-operation ordering.
- Existing package unit tests.
- `git diff --check`.
- Production review entrypoint against the working tree.

POSIX runtime install tests remain skipped on Windows when only the WSL shim is available. The static guard tests are intentionally platform-independent so this safety contract is still checked in the current environment.
