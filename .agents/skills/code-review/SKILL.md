---
name: code-review
description: Use when reviewing changes for bugs, regressions, security issues, missing tests, architectural drift, or unsafe cross-layer edits.
---

# Code Review

Use this skill when reviewing a change set before merge, release, or handoff.

## Default Stance

- Review for correctness first, not style.
- Stay read-only unless explicitly asked to patch findings.
- Prioritize bugs, regressions, unsafe assumptions, and missing validation.
- Treat architectural boundary violations as real risks, not “just refactor later”.

## Review Order

1. Understand the intended behavior and changed scope.
2. Check whether the implementation matches that intent.
3. Check whether layer boundaries and contracts were preserved.
4. Check whether tests cover the risky seams.
5. Check rollout, migration, and operational risk if the change touches persistence or infrastructure.

## Severity

- Critical: likely production breakage, data loss, security issue, or unrecoverable rollout risk.
- High: clear correctness bug, broken transaction behavior, broken API contract, or major regression risk.
- Medium: missing validation, incomplete error handling, fragile logic, or important test gap.
- Low: maintainability issue, minor inconsistency, or non-blocking cleanup.

## Backend Review Rubric

- Controllers stay thin and do not hold business logic.
- Services own use-case orchestration and business decisions.
- Repositories do not leak sessions upward or call `commit()` themselves.
- Write flows use an explicit Unit of Work and rollback path.
- DTOs remain separate from ORM models and transport glue.
- Exceptions are explicit and mapped cleanly at the FastAPI boundary.
- Dishka wiring uses sensible scopes and does not create hidden lifecycle bugs.
- Logging is structured, useful, and does not leak secrets.
- Alembic or schema changes preserve compatibility and rollback reality.

## Frontend Review Rubric

- Existing components or `shadcn/ui` pieces are reused before inventing new primitives.
- Route and container code stay thin; network logic is not buried in presentation leaves.
- Query and mutation flows handle loading, error, success, and invalidation paths correctly.
- Forms use typed validation consistently and map backend errors sanely.
- Accessibility-sensitive behavior remains intact for dialogs, popovers, tabs, tables, and forms.
- Responsive behavior is preserved where the feature depends on it.

## Common Regression Patterns

- A controller now talks to a repository directly.
- A service now depends on FastAPI or HTTP concerns.
- A repository creates its own session or commits independently.
- A write flow mutates state without an explicit transaction boundary.
- Response DTOs silently changed and consumers were not updated.
- New exceptions are raised but never mapped to stable HTTP responses.
- Logs were added with raw payloads, secrets, or duplicate noise.
- A migration is destructive without staged compatibility.
- A query or mutation path changed without updating invalidation or empty/error states.
- New UI abstractions duplicate existing component-system patterns.

## Testing Review

- Check whether the tests cover the changed seam, not just nearby files.
- For backend writes, look for commit and rollback coverage.
- For API changes, look for response shape and error mapping coverage.
- For persistence changes, look for migration and repository verification.
- For frontend changes, look for behavior, accessibility, and async-state coverage where risk is non-trivial.
- If tests were not run, treat that as residual risk and say so explicitly.

## Review Output

Return findings first, ordered by severity.

For each finding include:
- severity
- affected file or area
- what is wrong
- why it matters
- what validation is missing if relevant

After findings, include:
- open questions or assumptions
- missing tests
- residual risks

If no findings are discovered, say so explicitly and still mention any remaining test or rollout gaps.
