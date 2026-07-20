---
name: test-debug
description: Use when reproducing bugs, isolating regressions, writing failing tests, debugging flaky behavior, or validating fixes across affected layers.
---

# Test Debug

Use this skill when a bug needs to be reproduced, narrowed, and verified instead of guessed at.

## Goals

- Reproduce the problem before changing behavior when practical.
- Narrow the failure to the smallest meaningful seam.
- Prefer verification that would catch the regression again later.

## Default Workflow

1. Clarify the expected behavior, actual behavior, and affected layer.
2. Confirm the relevant environment assumptions first: settings profile, DB and migration target for persistence, API/runtime target for frontend, and local versus CI path.
3. Reproduce with the smallest reliable command, request, fixture, or UI path.
4. Decide the best seam for validation: unit/service, repository, API, composable, component, integration, or browser flow.
5. Add a failing test first when that is practical and stable.
6. Instrument only as much as needed to localize the failure.
7. Fix the issue at the correct layer.
8. Re-run the failing case, adjacent edge cases, and the smallest relevant regression suite.

## Rules

- Do not widen the fix before understanding the failing path.
- Prefer deterministic reproduction over anecdotal “seems fixed”.
- If the bug is flaky, capture the suspected timing, state, or environment factors explicitly.
- If the bug may depend on env drift, record the active config, DB target, and any local-versus-CI difference before patching code.
- For persistence-affecting work, treat a wrong or ambiguous DB target as a blocker, not as a note to mention later.
- Keep application code free of concrete infrastructure imports while diagnosing; do not turn temporary instrumentation into a boundary violation.
- If tests are too expensive or unavailable, describe the manual verification path clearly.

## Backend Guidance

- Check controller, service, repository, DTO, exception, and UoW boundaries in that order when the failure spans layers.
- For architecture or refactor regressions, audit direct infrastructure imports and broad UoW callsites in the touched service family before patching behavior.
- For write bugs, verify commit and rollback behavior.
- For schema-related bugs, confirm the active migration state and data assumptions.
- For DI or boundary bugs, confirm which provider or factory is actually supplying the service dependency at runtime.
- Run persistence reproduction only against an isolated test database or transaction scope with a fail-fast guard against dev and shared targets.

## Frontend Guidance

- Locate ownership first: component/view, composable, typed data access, schema/form, Pinia client state, or backend contract.
- Distinguish server state from client-owned and local UI state before changing a store or cache.
- For async regressions, inspect request keys, cancellation, response ordering, refresh/invalidation, optimistic rollback, and duplicate-submit behavior.
- Reproduce loading, empty, error, success, retry, disabled, and stale-data states that can hide the defect.
- Compare the runtime response and error body with OpenAPI, client types, form schema, and backend error mapping when contracts may have drifted.
- For UI interaction bugs, verify semantic elements, labels, focus movement, keyboard behavior, and responsive layout at the affected breakpoint.
- Avoid fixing a presentation symptom by adding transport logic to a leaf component or duplicating server state in Pinia.

## Browser Conditionality

- Use `agent-browser` only when it is installed and a real DOM, navigation, download, screenshot, login, or browser-runtime path is the smallest reliable reproduction seam.
- Prefer a unit, composable, component, API, or integration test for logic that does not require browser behavior.
- When browser automation is unavailable, use the project's native end-to-end runner or document an exact manual path; do not imply browser verification ran.
- Keep captured auth state, credentials, screenshots, traces, and downloads out of source control unless the project explicitly provides a safe artifact path.

## Verification Checklist

- original failing case
- adjacent edge cases
- environment plus DB, API, or browser target used for verification as relevant
- any fail-fast test DB safeguard that was checked or updated
- error mapping and logs if relevant
- provider or factory wiring if the bug crossed DI or transaction boundaries
- contract compatibility if the fix changed public shapes
- any migration or rollout concern if persistence changed
- frontend state ownership and refresh/invalidation behavior if client data changed
- accessibility and responsive states if interaction or layout changed
- browser command or explicit browser-verification gap when a real UI flow was material

## Handoff

Return:
- repro status
- failing case or why it could not be reproduced
- validation seam chosen
- environment assumptions checked
- tests added or run
- residual risks
