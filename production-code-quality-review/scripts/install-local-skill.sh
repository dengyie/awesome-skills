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

write_source_metadata() {
  local target_dir="$1"
  printf '%s\n' "$SOURCE_DIR" >"$target_dir/$SOURCE_METADATA_FILE"
}

copy_skill_tree "$SOURCE_DIR" "$TARGET_DIR"
write_source_metadata "$TARGET_DIR"

echo "Installed production-code-quality-review to $TARGET_DIR"

if [[ "$SYNC_LEGACY_COPY" == "1" ]]; then
  copy_skill_tree "$SOURCE_DIR" "$LEGACY_TARGET_DIR"
  write_source_metadata "$LEGACY_TARGET_DIR"
  echo "Synced legacy Codex skill copy to $LEGACY_TARGET_DIR"
fi
