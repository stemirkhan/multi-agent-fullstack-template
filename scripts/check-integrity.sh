#!/usr/bin/env bash
# Canonical integrity entrypoint for local development and CI.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/scripts/validate_template.py" --root "$ROOT"
