#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TARGET_DIR="$HOME/.agents/skills"

mkdir -p "$TARGET_DIR"

for skill_dir in "$REPO_DIR"/.agents/skills/*; do
  skill_name=$(basename "$skill_dir")
  rm -rf "$TARGET_DIR/$skill_name"
  cp -R "$skill_dir" "$TARGET_DIR/$skill_name"
done

echo "Codex skills installed into $TARGET_DIR"
