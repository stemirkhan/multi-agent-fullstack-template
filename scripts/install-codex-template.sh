#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /absolute/path/to/target-project" >&2
  exit 1
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TARGET_DIR=$1

if [ ! -d "$TARGET_DIR" ]; then
  echo "Target directory does not exist: $TARGET_DIR" >&2
  exit 1
fi

rm -rf "$TARGET_DIR/.codex" "$TARGET_DIR/.agents" "$TARGET_DIR/stack" "$TARGET_DIR/workflows"
cp -R "$REPO_DIR/.codex" "$TARGET_DIR/.codex"
cp -R "$REPO_DIR/.agents" "$TARGET_DIR/.agents"
cp -R "$REPO_DIR/stack" "$TARGET_DIR/stack"
cp -R "$REPO_DIR/workflows" "$TARGET_DIR/workflows"

echo "Official Codex project template installed into $TARGET_DIR"
