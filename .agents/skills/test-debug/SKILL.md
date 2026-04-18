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
2. Confirm the effective environment assumptions first: settings profile, `DATABASE_URL`, migration target, and local versus CI path.
3. Reproduce with the smallest reliable command, request, fixture, or UI path.
4. Decide the best seam for validation: unit, integration, API, or repository.
5. Add a failing test first when that is practical and stable.
6. Instrument only as much as needed to localize the failure.
7. Fix the issue at the correct layer.
8. Re-run the failing case and nearby regression checks.

## Rules

- Do not widen the fix before understanding the failing path.
- Prefer deterministic reproduction over anecdotal “seems fixed”.
- If the bug is flaky, capture the suspected timing, state, or environment factors explicitly.
- If the bug may depend on env drift, record the active config, DB target, and any local-versus-CI difference before patching code.
- Treat a wrong or ambiguous DB target as a blocker, not as a note to mention later.
- If tests are too expensive or unavailable, describe the manual verification path clearly.

## Backend Guidance

- Check controller, service, repository, DTO, exception, and UoW boundaries in that order when the failure spans layers.
- For architecture or refactor regressions, audit direct infrastructure imports and broad UoW callsites in the touched service family before patching behavior.
- For write bugs, verify commit and rollback behavior.
- For schema-related bugs, confirm the active migration state and data assumptions.
- For DI or boundary bugs, confirm which provider or factory is actually supplying the service dependency at runtime.

## Verification Checklist

- original failing case
- adjacent edge cases
- environment and DB target used for verification
- any fail-fast test DB safeguard that was checked or updated
- error mapping and logs if relevant
- provider or factory wiring if the bug crossed DI or transaction boundaries
- contract compatibility if the fix changed public shapes
- any migration or rollout concern if persistence changed

## Handoff

Return:
- repro status
- failing case or why it could not be reproduced
- validation seam chosen
- environment assumptions checked
- tests added or run
- residual risks
