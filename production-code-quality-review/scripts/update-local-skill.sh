#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
default_target_root="${AGENTS_HOME:-$HOME/.agents}"
TARGET_DIR="${SKILL_INSTALL_DIR:-$default_target_root/skills}/production-code-quality-review"
LEGACY_TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills/production-code-quality-review"
SYNC_LEGACY_COPY="${INSTALL_LEGACY_CODEX_COPY:-0}"
SOURCE_METADATA_FILE=".skill-source-dir"

copy_skill_tree() {
  local source_dir="$1"
  local target_dir="$2"

  rm -rf "$target_dir"
  mkdir -p "$(dirname "$target_dir")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude '.skill-source-dir' \
      --exclude '__pycache__/' \
      --exclude '*.pyc' \
      "$source_dir/" "$target_dir/"
  else
    cp -R "$source_dir" "$target_dir"
    find "$target_dir" \( -name '__pycache__' -type d -prune -o -name '*.pyc' -type f \) -exec rm -rf {} +
    rm -f "$target_dir/.skill-source-dir"
  fi
}

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

copy_skill_tree "$SOURCE_ROOT" "$TARGET_DIR"
printf '%s\n' "$SOURCE_ROOT" >"$TARGET_DIR/$SOURCE_METADATA_FILE"

echo "Updated production-code-quality-review in $TARGET_DIR"

if [[ "$SYNC_LEGACY_COPY" == "1" ]]; then
  copy_skill_tree "$SOURCE_ROOT" "$LEGACY_TARGET_DIR"
  printf '%s\n' "$SOURCE_ROOT" >"$LEGACY_TARGET_DIR/$SOURCE_METADATA_FILE"
  echo "Synced legacy Codex skill copy to $LEGACY_TARGET_DIR"
fi
