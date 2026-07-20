---
name: codex-review-loop
description: Use when the user wants a deep PR, branch, or uncommitted-change review through Codex CLI, with structured findings and an optional fix loop.
---

# Codex Review Loop

Use this skill when a normal read-only review is not enough and the user wants
an adversarial Codex CLI audit of a PR, branch diff, or local working tree.

## Inputs

- `--pr <N>` for a GitHub pull request whose exact head commit is currently checked out
- `--base <branch>` for a branch diff against a base
- `--uncommitted` for the current working tree

## Workflow

1. Resolve the review scope and base commit.
2. Run `scripts/codex-subagent.sh` to execute `codex exec review` in a read-only sandbox.
3. Validate the final response with `references/schemas/review-findings.schema.json`.
4. Cross-check findings against:
   - `.agents/skills/code-review/SKILL.md`
   - `.agents/skills/project-conventions/conventions.md`
   - `stack/default-stack.yaml`
5. Present findings first. Only enter a fix loop if the user explicitly wants it.
6. After fixes, re-run targeted verification and optionally a second review pass.

## References

- `references/prompts/adversarial-review.md`
- `references/schemas/review-findings.md`
- `references/schemas/review-findings.schema.json`
- `.agents/skills/code-review/SKILL.md`
- `.agents/skills/project-conventions/conventions.md`

## Notes

- `codex` CLI is required.
- `gh` is required only for `--pr`; the script verifies that the exact PR head commit is checked out and reviews against the exact PR base OID, refusing stale or unavailable objects.
- Python 3 is used for a local validation pass over the JSON returned by Codex; invalid or schema-incompatible output is rejected.
- Review mode stays read-only. Workspace-write access belongs to a separate, explicitly requested fix pass.
- Prefer repo-native lint, type-check, and test commands over hard-coded commands.
