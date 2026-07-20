#!/usr/bin/env bash
set -euo pipefail

# Read-only wrapper around `codex exec review` with structured output.
#
# Examples:
#   bash .agents/skills/codex-review-loop/scripts/codex-subagent.sh --base main
#   bash .agents/skills/codex-review-loop/scripts/codex-subagent.sh --uncommitted
#   cat .agents/skills/codex-review-loop/references/prompts/adversarial-review.md | \
#     bash .agents/skills/codex-review-loop/scripts/codex-subagent.sh --uncommitted

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCHEMA="$SKILL_DIR/references/schemas/review-findings.schema.json"
OUTPUT_VALIDATOR="$SCRIPT_DIR/validate-review-output.py"

REVIEW_ARGS=()
TARGET_COUNT=0
PR_NUMBER=""
CUSTOM_PROMPT=""

usage() {
  cat <<'EOF'
Usage: codex-subagent.sh (--base BRANCH | --commit SHA | --uncommitted | --pr N) [--prompt TEXT]

Environment:
  CODEX_REVIEW_MODEL       Optional model override.
  CODEX_REVIEW_REASONING   Optional model_reasoning_effort override.
EOF
}

require_value() {
  if [[ $# -lt 2 || -z "$2" ]]; then
    echo "Missing value for $1" >&2
    usage >&2
    exit 2
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base|--commit)
      require_value "$@"
      REVIEW_ARGS+=("$1" "$2")
      TARGET_COUNT=$((TARGET_COUNT + 1))
      shift 2
      ;;
    --uncommitted)
      REVIEW_ARGS+=("$1")
      TARGET_COUNT=$((TARGET_COUNT + 1))
      shift
      ;;
    --pr)
      require_value "$@"
      PR_NUMBER="$2"
      TARGET_COUNT=$((TARGET_COUNT + 1))
      shift 2
      ;;
    --prompt)
      require_value "$@"
      CUSTOM_PROMPT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ $TARGET_COUNT -ne 1 ]]; then
  echo "Choose exactly one review target." >&2
  usage >&2
  exit 2
fi

if [[ -n "$PR_NUMBER" ]]; then
  if [[ ! "$PR_NUMBER" =~ ^[1-9][0-9]*$ ]]; then
    echo "The --pr value must be a positive integer." >&2
    exit 2
  fi
  if ! command -v gh >/dev/null 2>&1; then
    echo "The --pr mode requires the gh CLI." >&2
    exit 2
  fi

  set +e
  PR_METADATA=$(gh pr view "$PR_NUMBER" \
      --json baseRefName,baseRefOid,headRefName,headRefOid \
      --jq '[.baseRefName, .baseRefOid, .headRefName, .headRefOid] | @tsv')
  GH_EXIT=$?
  set -e
  if [[ $GH_EXIT -ne 0 ]]; then
    echo "Could not query metadata for PR #$PR_NUMBER (gh exit $GH_EXIT)." >&2
    exit $GH_EXIT
  fi
  IFS=$'\t' read -r PR_BASE PR_BASE_OID PR_HEAD PR_HEAD_OID <<< "$PR_METADATA"
  if [[ -z "$PR_BASE" || -z "$PR_BASE_OID" || -z "$PR_HEAD" || -z "$PR_HEAD_OID" ]]; then
    echo "Could not resolve complete base/head metadata for PR #$PR_NUMBER." >&2
    exit 2
  fi
  if [[ ! "$PR_BASE_OID" =~ ^[0-9a-fA-F]{40,64}$ || ! "$PR_HEAD_OID" =~ ^[0-9a-fA-F]{40,64}$ ]]; then
    echo "PR #$PR_NUMBER returned malformed base/head object IDs." >&2
    exit 2
  fi
  CURRENT_OID="$(git rev-parse HEAD)"
  if [[ "$CURRENT_OID" != "$PR_HEAD_OID" ]]; then
    echo "PR #$PR_NUMBER head '$PR_HEAD' is $PR_HEAD_OID, but current HEAD is $CURRENT_OID." >&2
    echo "Check out the exact PR head commit before reviewing." >&2
    exit 2
  fi
  if ! git cat-file -e "${PR_BASE_OID}^{commit}" 2>/dev/null; then
    echo "PR #$PR_NUMBER base '$PR_BASE' commit $PR_BASE_OID is not available locally." >&2
    echo "Fetch the exact base commit, then retry the review." >&2
    exit 2
  fi
  REVIEW_ARGS+=("--base" "$PR_BASE_OID")
fi

EXEC_ARGS=("exec" "--sandbox" "read-only" "--ephemeral")

if [[ -n "${CODEX_REVIEW_MODEL:-}" ]]; then
  EXEC_ARGS+=("-m" "$CODEX_REVIEW_MODEL")
fi

if [[ -n "${CODEX_REVIEW_REASONING:-}" ]]; then
  EXEC_ARGS+=("-c" "model_reasoning_effort=\"$CODEX_REVIEW_REASONING\"")
fi

if [[ -n "$CUSTOM_PROMPT" ]]; then
  REVIEW_ARGS+=("$CUSTOM_PROMPT")
elif [[ -p /dev/stdin ]]; then
  REVIEW_ARGS+=("-")
fi

set +e
OUTPUT=$(codex "${EXEC_ARGS[@]}" review --output-schema "$SCHEMA" "${REVIEW_ARGS[@]}")
EXIT_CODE=$?
set -e

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "Codex review failed (exit $EXIT_CODE):" >&2
  printf '%s\n' "$OUTPUT" >&2
  exit $EXIT_CODE
fi

if ! printf '%s' "$OUTPUT" | python3 "$OUTPUT_VALIDATOR" "$SCHEMA"; then
  echo "Codex review returned output that does not match the findings schema." >&2
  exit 2
fi

printf '%s\n' "$OUTPUT"
