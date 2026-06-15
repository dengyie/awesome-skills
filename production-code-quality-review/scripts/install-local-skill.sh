#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_target_root="${AGENTS_HOME:-$HOME/.agents}"
TARGET_DIR="${SKILL_INSTALL_DIR:-$default_target_root/skills}/production-code-quality-review"
LEGACY_TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills/production-code-quality-review"
SYNC_LEGACY_COPY="${INSTALL_LEGACY_CODEX_COPY:-0}"
SOURCE_METADATA_FILE=".skill-source-dir"

write_source_metadata() {
  local target_dir="$1"
  printf '%s\n' "$SOURCE_DIR" >"$target_dir/$SOURCE_METADATA_FILE"
}

rm -rf "$TARGET_DIR"
mkdir -p "$(dirname "$TARGET_DIR")"
cp -R "$SOURCE_DIR" "$TARGET_DIR"
write_source_metadata "$TARGET_DIR"

echo "Installed production-code-quality-review to $TARGET_DIR"

if [[ "$SYNC_LEGACY_COPY" == "1" ]]; then
  rm -rf "$LEGACY_TARGET_DIR"
  mkdir -p "$(dirname "$LEGACY_TARGET_DIR")"
  cp -R "$SOURCE_DIR" "$LEGACY_TARGET_DIR"
  write_source_metadata "$LEGACY_TARGET_DIR"
  echo "Synced legacy Codex skill copy to $LEGACY_TARGET_DIR"
fi
