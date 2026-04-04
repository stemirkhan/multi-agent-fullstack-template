---
name: frontend-data-access
description: Use when implementing typed API clients, Nuxt data-loading flows, writes, refresh strategy, or server-state boundaries in the TypeScript frontend.
---

# Frontend Data Access

Use this skill when frontend code needs to fetch, mutate, refresh, or synchronize server state.

## Responsibilities

- Keep API clients typed and predictable.
- Encapsulate read and write behavior behind focused composables, feature modules, or server utilities.
- Make refresh strategy and server-state synchronization explicit.
- Prevent transport details from leaking into presentation-only components.

## Default Structure

- One thin API client layer for request construction and response typing.
- Composables or useAsyncData or useFetch wrappers for read flows.
- Focused write actions, usually via typed client helpers or feature composables.
- Feature code composes those seams and maps them into UI behavior.

## Rules

- Prefer typed request and response contracts.
- Keep cache keys, async-data keys, and refresh boundaries stable and intention-revealing.
- Do not scatter fetch calls directly across pages and leaf components.
- Handle loading, empty, error, and success states deliberately.
- Keep retries, lazy loading, and refresh behavior explicit where they affect UX.

## Refresh And Synchronization Guidance

- Refresh the smallest correct scope after writes.
- Prefer targeted local updates when the new state is fully known and low-risk.
- Avoid stale UI by refreshing or invalidating dependent async-data surfaces after a write.
- Document optimistic updates clearly and keep rollback behavior explicit.

## Mutation Guidance

- Surface pending and failure state to the UI.
- Map backend validation or conflict errors into a shape the form or feature layer can use.
- Do not bury toasts, redirects, and UI transitions inside the raw API client.
- Keep side effects near the feature boundary, composable, or store action that owns them.

## Error Handling

- Normalize transport and contract failures enough for the UI to react consistently.
- Keep user-facing messaging separate from low-level response parsing where possible.
- Do not swallow errors that should affect UX or telemetry.
- Keep Nuxt server/client execution context explicit when handling auth, cookies, or environment-specific behavior.

## Verification

- Test async-data keys, refresh behavior, and invalidation boundaries for non-trivial changes.
- Test optimistic updates or post-write local updates when used.
- Test important loading and error states at the feature level.
- Verify contract changes stay aligned with backend DTOs and generated clients if used.

## Handoff

Return:
- clients, composables, or write paths added or changed
- async-data keys and refresh strategy
- optimistic update or rollback notes
- frontend/backend contract dependencies
- tests run
