# Review Findings Schema

Use this field reference when reading structured review output. The executable
contract lives in `review-findings.schema.json` and is passed to Codex through
`--output-schema`. The wrapper also validates the returned JSON locally before
printing it, so a CLI or transport regression cannot silently bypass the contract.

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | Yes | Finding identifier such as `P1` |
| `severity` | `enum` | Yes | `Critical` \| `High` \| `Medium` \| `Low` |
| `category` | `enum` | Yes | `security` \| `bug` \| `typing` \| `architecture` \| `testing` \| `performance` \| `compatibility` \| `convention` |
| `file` | `string` | Yes | Relative file path or affected area |
| `lines` | `string` | No | Line number or range when available |
| `title` | `string` | Yes | One-line summary |
| `description` | `string` | Yes | What is wrong and why it matters |
| `suggestion` | `string` | No | Specific fix direction or code-oriented suggestion |
| `impact` | `string` | No | Consequence if left unresolved |
| `effort` | `enum` | No | `trivial` \| `small` \| `medium` \| `large` |
| `status` | `enum` | Yes | `pending` \| `approved` \| `fixed` \| `skipped` \| `wont-fix` |

## Severity Definitions

| Severity | Meaning |
|----------|---------|
| `Critical` | Security vulnerability, data loss, production breakage, or unrecoverable rollout risk |
| `High` | Clear correctness bug, broken contract, or likely CI or runtime failure |
| `Medium` | Maintainability issue, missing validation, or important test gap |
| `Low` | Minor cleanup, documentation, or low-risk consistency issue |

## Category Definitions

| Category | Meaning |
|----------|---------|
| `security` | Auth, secret handling, injection, or trust-boundary issue |
| `bug` | Functional defect or broken logic |
| `typing` | Type drift, missing typed boundary, or schema mismatch |
| `architecture` | Layer violation, DI misuse, or ownership boundary erosion |
| `testing` | Missing or stale test coverage for changed behavior |
| `performance` | Wasteful query, blocking path, or inefficient update pattern |
| `compatibility` | Backward-compatibility or consumer-breakage risk |
| `convention` | Violation of repo-local conventions or stack contract |

## Effort Definitions

| Effort | Meaning |
|--------|---------|
| `trivial` | 1-2 line change |
| `small` | Small isolated fix |
| `medium` | Multi-line or multi-function fix |
| `large` | Multi-file or structural refactor |

## Status Lifecycle

`pending -> approved -> fixed`

Possible alternate outcomes:
- `pending -> wont-fix`
- `approved -> skipped`

## Example

```markdown
| # | Sev | Category | File:Line | Title | Effort | Status |
|---|-----|----------|-----------|-------|--------|--------|
| P1 | High | architecture | app/service.py:42 | Repository commit bypasses unit of work | small | pending |
| P2 | Medium | testing | web/src/features/user/form.ts:88 | Submit path changed without invalid-state test | small | pending |
```
