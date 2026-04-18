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
- Services do not import or construct concrete infrastructure UoW or session types.
- Application modules do not import infrastructure implementations, DI wiring, raw HTTP clients, or ORM models directly.
- Repositories do not leak sessions upward or call `commit()` themselves.
- Write flows use an explicit Unit of Work and rollback path.
- UoW factory and DI wiring preserve the intended `async with` lifecycle and rollback semantics.
- Shared UoW or repository surfaces have not grown when a family-port extraction should have happened first.
- DTOs remain separate from ORM models and transport glue.
- Exceptions are explicit and mapped cleanly at the FastAPI boundary.
- Dishka wiring uses sensible scopes and does not create hidden lifecycle bugs.
- Logging is structured, useful, and does not leak secrets.
- Alembic or schema changes preserve compatibility and rollback reality.
- Test and CI paths use an isolated test profile and do not silently point at an app database.
- If the repo includes agent scaffolding, check parity across `agents/roles`, `.codex/agents`, `workflows/`, and integrity scripts.

## Common Regression Patterns

- A controller now talks to a repository directly.
- A service now depends on FastAPI or HTTP concerns.
- A service now constructs `SqlAlchemyUnitOfWork`, `AsyncSession`, or another concrete infra boundary directly.
- A broad `uow.foo` or repository surface grew even though the change only touched one capability family.
- A repository creates its own session or commits independently.
- A write flow mutates state without an explicit transaction boundary.
- A UoW factory returns an object that skips the expected `__aenter__` or `__aexit__` behavior.
- A write-oriented port absorbed read-model assembly or DTO projection logic that should have stayed on a reader seam.
- Response DTOs silently changed and consumers were not updated.
- New exceptions are raised but never mapped to stable HTTP responses.
- Logs were added with raw payloads, secrets, or duplicate noise.
- A migration is destructive without staged compatibility.
- Tests or CI run against a shared app database or the wrong settings profile.
- A new feature was appended to a generic file like `auth.py`, `models.py`, or `settings.py` even though it introduced a new use-case family or bounded context.
- A refactor moved symbols across modules without keeping a compatibility facade for stable imports.
- Tests remained in a generic bucket even after the runtime code was clearly organized by domain.

## Architectural Growth Review

- Flag files that keep accumulating unrelated responsibilities even if the code inside them is locally correct.
- Treat “wrong landing zone” as a maintainability risk when the repo already has clearer domain boundaries available.
- Call out missing structural-prep work when a feature should have started with a split before implementation.
- Treat deferred port extraction or hidden boundary surgery inside a behavior patch as a review finding, not as harmless cleanup debt.

## Testing Review

- Check whether the tests cover the changed seam, not just nearby files.
- For backend writes, look for commit and rollback coverage.
- For DI or boundary refactors, look for provider or factory coverage through the abstract interface used by services.
- For API changes, look for response shape and error mapping coverage.
- For persistence changes, look for migration and repository verification.
- If CI or local test entrypoints changed, check that the effective DB target is still a dedicated test database.
- For persistence-affecting refactors, verify the test DB safeguard or fail-fast guard still prevents accidental use of dev or shared app databases.
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
