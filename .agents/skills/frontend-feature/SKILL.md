---
name: frontend-feature
description: Use when implementing or modifying TypeScript Vue and Nuxt features with typed API access, composables, form handling, and frontend best practices.
---

# Frontend Feature

Use this skill as the top-level frontend orchestrator when a change spans components, composables, data access, forms, and page-level behavior.

## Purpose

- Turn one frontend feature request into a coherent set of UI, state, and integration changes.
- Keep the implementation aligned with the stack contract: TypeScript-first Vue, `Nuxt`, `Pinia`, explicit composables, and schema-driven validation.
- Decide which lower-level frontend skills are needed and in what order to apply them.

## Load Related Skills As Needed

- `vue` for component, composable, and feature structure.
- `nuxt` for routing, data loading, app structure, and server/client boundaries.
- `pinia` for shared cross-route state when a composable is not enough.
- `web-design-guidelines` for reusable UI and accessible component composition.
- `frontend-data-access` for API clients, async data flows, refresh strategy, and writes.
- `frontend-forms-and-validation` for forms, schemas, and backend error mapping.
- `api-contracts` when frontend contracts or generated clients change.
- `test-debug` when reproducing UI regressions or validating risky async behavior.

## Default Build Order

1. Clarify the user-facing workflow, page surface, async states, and acceptance criteria.
2. Identify affected contracts: props, query params, form schema, response shape, and API dependencies.
3. Decide whether the feature is mostly display, mostly form-driven, mostly async state coordination, or shared client state.
4. Implement or update typed API utilities, composables, and client contracts first when server interaction is central.
5. Implement feature-level logic and component composition next.
6. Add or update forms and validation wiring where user input is involved.
7. Use existing design-system components before extending or creating new primitives.
8. Verify loading, empty, error, success, hydration, and responsive states.
9. Add or update tests at the right seam: composable, component, store, flow, or integration.

## Core Rules

- Start from the user workflow, not from isolated markup.
- Keep network access and write orchestration out of presentation-only leaves.
- Keep pages thin; push reusable behavior into composables, stores, or feature modules.
- Prefer typed boundaries over loosely shaped objects and `any`.
- Preserve accessibility and interaction semantics when customizing component behavior.
- Reuse existing UI building blocks before creating new abstractions.

## Common Change Patterns

- New page or route:
  data access -> composable -> composed UI -> loading/error states -> tests
- New form:
  schema -> form wiring -> submit handler -> backend error mapping -> success state -> tests
- New async interaction:
  write utility or action -> refresh or update strategy -> UI feedback -> tests
- Contract-driven change:
  API client -> composable or store -> component props and rendering -> tests

## Definition Of Done

- Type boundaries are explicit.
- UI is built from existing component-system pieces where reasonable.
- Async states are handled coherently.
- Forms validate predictably and map backend failures clearly.
- Accessibility, hydration safety, and responsive behavior are preserved.
- Tests cover the changed feature seam.

## Handoff

Return:
- routes or feature surfaces touched
- components introduced or extended
- composable, store, or async-data flows changed
- form and validation notes
- contract dependencies affected
- tests run
