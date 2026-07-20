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
- If the repo includes agent scaffolding, check parity across `.codex/agents`, the shared skills layer, workflows, project templates, and integrity scripts.

## Frontend Review Rubric

- Route views and screen-level components stay thin; presentation leaves do not own transport or cross-feature orchestration.
- Props, emits, slots, composables, store actions, and API clients remain explicitly typed without avoidable `any` or silent coercion.
- Server state, request status, refresh, and invalidation stay in data-access/query seams; Pinia is reserved for shared client-owned state.
- Local presentation and form state has not been promoted to a store without a real cross-feature ownership need.
- Async flows handle relevant loading, empty, error, success, disabled, retry, stale-response, and duplicate-submit states.
- Writes define refresh, invalidation, optimistic update, and rollback behavior so dependent views cannot silently stay stale.
- Forms use one schema and preserve backend validation, conflict, forbidden, and form-level error semantics.
- Components reuse the existing design system and preserve semantic HTML, labels, focus behavior, keyboard access, and responsive states.
- Browser-only APIs, cookies, tokens, and storage have an explicit ownership boundary and do not expose secrets or privileged policy in the client.
- Untrusted content remains escaped or passes through an intentional, tested sanitization boundary.

## Contract And Operational Review

- Request, response, route, status, header, authentication, pagination, enum, nullability, default, and documented error changes are reflected in emitted OpenAPI and affected typed consumers.
- Generated schemas or clients are refreshed and drift checks remain effective when the project uses generation.
- Authentication and authorization remain enforced by the backend rather than inferred from hidden UI controls.
- Logs and telemetry preserve useful correlation and machine-readable errors without sensitive payloads or duplicate noise.

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
- A leaf component now fetches, mutates, redirects, and renders in one coupled path.
- Server responses or request status were copied into Pinia, creating two caches without an invalidation policy.
- A write succeeds but dependent queries, stores, or views remain stale.
- A form duplicates its schema or flattens every backend failure into one generic message.
- A component change breaks focus, keyboard interaction, labels, responsive layout, or an async state that the happy path hides.
- Client code stores sensitive credentials, trusts UI-only authorization, or renders unsanitized untrusted HTML.

## Architectural Growth Review

- Flag files that keep accumulating unrelated responsibilities even if the code inside them is locally correct.
- Treat “wrong landing zone” as a maintainability risk when the repo already has clearer domain boundaries available.
- Call out missing structural-prep work when a feature should have started with a split before implementation.
- Treat deferred port extraction or hidden boundary surgery inside a behavior patch as a review finding, not as harmless cleanup debt.
- Apply the same test to frontend growth: split a view, composable, store, or data-access module before it absorbs a second unrelated feature family.

## Testing Review

- Check whether the tests cover the changed seam, not just nearby files.
- For backend writes, look for commit and rollback coverage.
- For DI or boundary refactors, look for provider or factory coverage through the abstract interface used by services.
- For API changes, look for response shape and error mapping coverage.
- For persistence changes, look for migration and repository verification.
- If CI or local test entrypoints changed, check that the effective DB target is still a dedicated test database.
- For persistence-affecting refactors, verify the test DB safeguard or fail-fast guard still prevents accidental use of dev or shared app databases.
- For frontend data changes, look for refresh/invalidation, race, stale-response, optimistic rollback, and error-state coverage.
- For component and form changes, look for interaction, accessibility, validation, duplicate-submit, and state-reset coverage.
- For shared-state changes, verify initialization, hydration if applicable, reset, and ownership boundaries.
- If tests were not run, treat that as residual risk and say so explicitly.

## Browser Validation

- Use browser automation only if `agent-browser` is installed and a real DOM, navigation, download, screenshot, login, or browser-runtime path is the smallest reliable validation seam.
- Prefer type checks and focused unit, composable, component, API, or integration tests for logic that does not require a browser.
- Treat browser evidence as complementary for risky flows, not as a substitute for deterministic regression coverage.
- If browser automation is unavailable but material UI risk remains, record the exact manual or project-native end-to-end verification gap.

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
