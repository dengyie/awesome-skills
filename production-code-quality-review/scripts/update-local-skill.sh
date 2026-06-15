#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
default_target_root="${AGENTS_HOME:-$HOME/.agents}"
TARGET_DIR="${SKILL_INSTALL_DIR:-$default_target_root/skills}/production-code-quality-review"
LEGACY_TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills/production-code-quality-review"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Skill not installed. Run install-local-skill.sh first." >&2
  exit 1
fi

rm -rf "$TARGET_DIR"
cp -R "$SOURCE_DIR" "$TARGET_DIR"

echo "Updated production-code-quality-review in $TARGET_DIR"

if [[ -d "$LEGACY_TARGET_DIR" ]] || [[ "${INSTALL_LEGACY_CODEX_COPY:-0}" == "1" ]]; then
  rm -rf "$LEGACY_TARGET_DIR"
  mkdir -p "$(dirname "$LEGACY_TARGET_DIR")"
  cp -R "$SOURCE_DIR" "$LEGACY_TARGET_DIR"
  echo "Synced legacy Codex skill copy to $LEGACY_TARGET_DIR"
fi
