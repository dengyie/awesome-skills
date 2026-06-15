#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills/production-code-quality-review"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Skill not installed. Run install-local-skill.sh first." >&2
  exit 1
fi

rm -rf "$TARGET_DIR"
cp -R "$SOURCE_DIR" "$TARGET_DIR"

echo "Updated production-code-quality-review in $TARGET_DIR"
