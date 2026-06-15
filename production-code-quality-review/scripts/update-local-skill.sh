#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
default_target_root="${AGENTS_HOME:-$HOME/.agents}"
TARGET_DIR="${SKILL_INSTALL_DIR:-$default_target_root/skills}/production-code-quality-review"
LEGACY_TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills/production-code-quality-review"
SYNC_LEGACY_COPY="${INSTALL_LEGACY_CODEX_COPY:-0}"
SOURCE_METADATA_FILE=".skill-source-dir"

read_source_metadata() {
  local metadata_file="$1/$SOURCE_METADATA_FILE"
  if [[ -f "$metadata_file" ]]; then
    tr -d '\n' <"$metadata_file"
  fi
}

SOURCE_ROOT="$(read_source_metadata "$TARGET_DIR")"
if [[ -z "$SOURCE_ROOT" ]]; then
  SOURCE_ROOT="$SOURCE_DIR"
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Skill not installed. Run install-local-skill.sh first." >&2
  exit 1
fi

if [[ ! -d "$SOURCE_ROOT" ]]; then
  echo "Unable to find the source checkout recorded by the installed skill." >&2
  exit 1
fi

rm -rf "$TARGET_DIR"
cp -R "$SOURCE_ROOT" "$TARGET_DIR"
printf '%s\n' "$SOURCE_ROOT" >"$TARGET_DIR/$SOURCE_METADATA_FILE"

echo "Updated production-code-quality-review in $TARGET_DIR"

if [[ "$SYNC_LEGACY_COPY" == "1" ]]; then
  rm -rf "$LEGACY_TARGET_DIR"
  mkdir -p "$(dirname "$LEGACY_TARGET_DIR")"
  cp -R "$SOURCE_ROOT" "$LEGACY_TARGET_DIR"
  printf '%s\n' "$SOURCE_ROOT" >"$LEGACY_TARGET_DIR/$SOURCE_METADATA_FILE"
  echo "Synced legacy Codex skill copy to $LEGACY_TARGET_DIR"
fi
