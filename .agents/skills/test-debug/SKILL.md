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
2. Reproduce with the smallest reliable command, request, fixture, or UI path.
3. Decide the best seam for validation: unit, integration, API, repository, UI, or e2e.
4. Add a failing test first when that is practical and stable.
5. Instrument only as much as needed to localize the failure.
6. Fix the issue at the correct layer.
7. Re-run the failing case and nearby regression checks.

## Rules

- Do not widen the fix before understanding the failing path.
- Prefer deterministic reproduction over anecdotal “seems fixed”.
- If the bug is flaky, capture the suspected timing, state, or environment factors explicitly.
- If tests are too expensive or unavailable, describe the manual verification path clearly.

## Backend Guidance

- Check controller, service, repository, DTO, exception, and UoW boundaries in that order when the failure spans layers.
- For write bugs, verify commit and rollback behavior.
- For schema-related bugs, confirm the active migration state and data assumptions.

## Frontend Guidance

- Reproduce at the user-visible flow level before diving into component internals.
- Check query, mutation, form, and component boundaries explicitly.
- Verify loading, empty, error, success, and responsive states when async behavior changed.

## Verification Checklist

- original failing case
- adjacent edge cases
- error mapping and logs if relevant
- contract compatibility if the fix changed public shapes
- any migration or rollout concern if persistence changed

## Handoff

Return:
- repro status
- failing case or why it could not be reproduced
- validation seam chosen
- tests added or run
- residual risks
