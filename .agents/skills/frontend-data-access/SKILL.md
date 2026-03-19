---
name: frontend-data-access
description: Use when implementing typed API clients, TanStack Query hooks, mutation flows, cache invalidation, or server-state boundaries in the TypeScript frontend.
---

# Frontend Data Access

Use this skill when frontend code needs to fetch, mutate, cache, or synchronize server state.

## Responsibilities

- Keep API clients typed and predictable.
- Encapsulate query and mutation behavior behind focused hooks or feature modules.
- Make cache invalidation and server-state synchronization explicit.
- Prevent transport details from leaking into presentation-only components.

## Default Structure

- One thin API client layer for request construction and response typing.
- Query hooks for read flows.
- Mutation hooks for write flows.
- Feature code composes those hooks and maps them into UI behavior.

## Rules

- Prefer typed request and response contracts.
- Keep query keys stable and intention-revealing.
- Do not scatter fetch calls directly across page and leaf components.
- Handle loading, empty, error, and success states deliberately.
- Keep retries, stale times, and background refetch behavior explicit where they affect UX.

## Cache Guidance

- Invalidate the smallest correct scope after mutations.
- Prefer targeted cache updates when the new state is fully known and low-risk.
- Avoid stale UI by forgetting dependent queries after a write.
- Document optimistic updates clearly and keep rollback behavior explicit.

## Mutation Guidance

- Surface pending and failure state to the UI.
- Map backend validation or conflict errors into a shape the form or feature layer can use.
- Do not bury toasts, redirects, and UI transitions inside the raw API client.
- Keep side effects near the mutation hook or feature boundary that owns them.

## Error Handling

- Normalize transport and contract failures enough for the UI to react consistently.
- Keep user-facing messaging separate from low-level response parsing where possible.
- Do not swallow errors that should affect UX or telemetry.

## Verification

- Test query keys and invalidation behavior for non-trivial changes.
- Test optimistic updates or post-mutation cache updates when used.
- Test important loading and error states at the feature level.
- Verify contract changes stay aligned with backend DTOs and generated clients if used.

## Handoff

Return:
- clients, queries, or mutations added or changed
- query keys and invalidation strategy
- optimistic update or rollback notes
- frontend/backend contract dependencies
- tests run
