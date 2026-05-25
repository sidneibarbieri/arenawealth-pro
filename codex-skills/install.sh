#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

mkdir -p "$TARGET_DIR"

for skill_dir in "$SOURCE_DIR"/*; do
  [[ -d "$skill_dir" ]] || continue
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  skill_name="$(basename "$skill_dir")"
  rm -rf "$TARGET_DIR/$skill_name"
  cp -R "$skill_dir" "$TARGET_DIR/$skill_name"
  echo "installed $skill_name"
done

if [[ -d "$SOURCE_DIR/scripts" ]]; then
  rm -rf "$TARGET_DIR/scripts"
  cp -R "$SOURCE_DIR/scripts" "$TARGET_DIR/scripts"
  echo "installed shared scripts"
fi

echo "Codex skills installed in $TARGET_DIR"
