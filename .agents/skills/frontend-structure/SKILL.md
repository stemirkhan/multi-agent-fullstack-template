---
name: frontend-structure
description: Use when you need to understand or plan the default frontend structure in the TypeScript Vue stack, decide where UI, composables, stores, and form logic belong, or map responsibilities across route views, features, typed API access, validation, and shared components.
---

# Frontend Structure

Use this skill to orient work in the default frontend architecture before editing Vue route views, feature modules, composables, stores, or shared UI.

## Purpose

- Map a frontend change to the correct feature, view, and shared-layer boundary.
- Keep changes aligned with `stack/default-stack.yaml`.
- Prevent view code, network logic, and presentation components from collapsing into one layer.

## Default Layer Map

- Route views and screen-level entry components: thin entry surfaces that read params, compose features, and own view-level concerns only.
- `vue`: component structure, props, emits, slots, composables, and typed Vue composition.
- `pinia`: shared cross-feature or cross-view state when local composables are not enough.
- `frontend-data-access`: typed API clients, composable read flows, writes, and refresh strategy.
- `frontend-forms-and-validation`: schema-driven validation, submission flow, and backend error mapping.
- `web-design-guidelines`: accessible UI composition and styling guidance built on the existing design system.
- `api-contracts`: client-facing contract alignment when request or response shapes change.
- `project-conventions`: repo-local implementation rules that refine the default stack contract.
- `test-debug`: regression isolation and validation for risky async or UI behavior.

## Placement Rules

- If the change is about route composition, params, or screen-level state, start at the route view or feature entry.
- If the change talks to the server, put typed clients and data-loading logic in composables or feature data-access modules, not in leaf components.
- If the change collects user input, define schema and form wiring explicitly instead of scattering validation across event handlers.
- If the change is visual, reuse the existing component system before creating custom primitives.
- If logic is reused across multiple screens, extract it into a composable or shared component after the second clear use case.
- Keep local UI state near the feature; avoid Pinia unless cross-feature coordination or durable client state is clearly required.
- Coordinate contract changes with typed API boundaries instead of passing loosely typed payloads through props.

## Default Interaction Flow

1. Route view, screen entry, or feature entry reads params and composes the workflow.
2. Composables or feature data-access modules load or mutate server state.
3. Forms use explicit schema validation and composable or project-standard form wiring when user input is involved.
4. Presentation components render loading, empty, error, and success states with the existing design system.
5. Writes refresh, update, or invalidate the smallest correct data surface and show user feedback intentionally.
6. Tests cover the changed seam at composable, component, store, or flow level.

## Smells

- Raw `fetch` or typed client calls inside leaf presentation components.
- Route-view files containing most of the feature logic.
- Untyped or loosely typed server payloads flowing through props.
- Validation duplicated between UI handlers and submit logic.
- Custom primitives replacing existing component-system pieces without a strong reason.
- Pinia stores used for request lifecycle problems or page-local state that fit composables or local state.

## Load Related Skills As Needed

- `frontend-feature` for end-to-end frontend delivery.
- `project-conventions`, `vue`, `pinia`, `frontend-data-access`, `frontend-forms-and-validation`, `web-design-guidelines`, `api-contracts`, and `test-debug` based on the affected seam.

## Handoff

Return:
- target route, feature, or shared layer
- likely modules or folders affected
- composable, store, and data-loading notes
- form or contract changes
- risks around async state, reuse, or coupling
