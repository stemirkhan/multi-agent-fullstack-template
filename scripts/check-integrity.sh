#!/usr/bin/env bash
# check-integrity.sh — validates cross-references in the fullstack template.
# Checks:
#   1. Paths in "Read before acting" blocks in .codex/agents/*.toml exist
#   2. Workflow role ids align with .codex agents via hyphen/underscore normalization
#   3. Copy-ready project AGENTS templates exist
# Usage: bash scripts/check-integrity.sh

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

fail() { echo "  FAIL: $1"; ERRORS=$((ERRORS + 1)); }
ok()   { echo "  ok:   $1"; }

echo "=== 1. 'Read before acting' paths in .codex/agents/*.toml ==="
while IFS= read -r toml_file; do
  python3 - "$toml_file" <<'PYEOF'
import sys, re

path = sys.argv[1]
lines = open(path).readlines()
in_block = False
for line in lines:
    stripped = line.rstrip()
    if re.search(r'[Rr]ead before acting', stripped):
        in_block = True
        continue
    if in_block and re.match(r'^\s*-\s+\S', stripped):
        print(re.sub(r'^\s*-\s+', '', stripped))
    elif in_block and stripped == '':
        in_block = False
PYEOF
done < <(find "$ROOT/.codex/agents" -name "*.toml") | sort -u | while IFS= read -r ref_path; do
  full="$ROOT/$ref_path"
  if [[ -f "$full" ]]; then
    ok "$ref_path"
  else
    fail "path '$ref_path' not found"
  fi
done

echo ""
echo "=== 2. Workflow and .codex agent alignment ==="
if python3 - "$ROOT" <<'PYEOF'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
codex_dir = root / ".codex" / "agents"
workflow_dir = root / "workflows"

errors: list[str] = []

def normalize(name: str) -> str:
    return name.replace("-", "_")

codex_names: dict[str, Path] = {}
for path in sorted(codex_dir.glob("*.toml")):
    text = path.read_text()
    match = re.search(r'^name\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if match is None:
        errors.append(f"{path.relative_to(root)} is missing a name field")
        continue
    codex_names[match.group(1)] = path

for path in sorted(workflow_dir.glob("*.yaml")):
    text = path.read_text()
    for role in re.findall(r"^\s+-\s+role:\s*([A-Za-z0-9_-]+)\s*$", text, re.MULTILINE):
        if normalize(role) not in codex_names:
            errors.append(
                f"{path.relative_to(root)} references unknown role '{role}'"
            )

if errors:
    for error in errors:
        print(f"  FAIL: {error}")
    raise SystemExit(1)

print("  ok:   workflows and .codex agents are aligned")
PYEOF
then
  :
else
  ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=== 3. Copy-ready project templates ==="
for path in \
  "templates/project-AGENTS.md" \
  "templates/project-AGENTS.backend.md" \
  "templates/project-AGENTS.frontend.md"
do
  if [[ -f "$ROOT/$path" ]]; then
    ok "$path"
  else
    fail "template '$path' not found"
  fi
done

echo ""
if [[ $ERRORS -eq 0 ]]; then
  echo "All checks passed."
  exit 0
else
  echo "$ERRORS integrity error(s) found."
  exit 1
fi
