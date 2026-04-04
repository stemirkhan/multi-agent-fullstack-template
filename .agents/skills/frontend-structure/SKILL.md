---
name: frontend-structure
description: Use when you need to understand or plan the default frontend structure in the TypeScript Vue and Nuxt stack, decide where UI, composables, stores, and form logic belong, or map responsibilities across pages, features, typed API access, validation, and shared components.
---

# Frontend Structure

Use this skill to orient work in the default frontend architecture before editing Nuxt pages, feature modules, composables, stores, or shared UI.

## Purpose

- Map a frontend change to the correct feature, route, and shared-layer boundary.
- Keep changes aligned with `stack/default-stack.yaml`.
- Prevent route code, network logic, and presentation components from collapsing into one layer.

## Default Layer Map

- Nuxt pages and layouts: thin entry surfaces that read params, compose features, and own page-level concerns only.
- `vue`: component structure, props, emits, slots, composables, and typed Vue composition.
- `nuxt`: route surfaces, server/client boundaries, data loading, and app-level conventions.
- `pinia`: shared cross-route state when local composables are not enough.
- `frontend-data-access`: typed API clients, useFetch or useAsyncData flows, writes, and refresh strategy.
- `frontend-forms-and-validation`: schema-driven validation, submission flow, and backend error mapping.
- `web-design-guidelines`: accessible UI composition and styling guidance built on the existing design system.
- `api-contracts`: client-facing contract alignment when request or response shapes change.
- `test-debug`: regression isolation and validation for risky async or UI behavior.

## Placement Rules

- If the change is about page composition, route params, middleware, or screen-level state, start at the Nuxt page, layout, or feature entry.
- If the change talks to the server, put typed clients and data-loading logic in composables, async-data seams, or server utilities, not in leaf components.
- If the change collects user input, define schema and form wiring explicitly instead of scattering validation across event handlers.
- If the change is visual, reuse the existing component system before creating custom primitives.
- If logic is reused across multiple screens, extract it into a composable or shared component after the second clear use case.
- Keep local UI state near the feature; avoid Pinia unless cross-route coordination or durable client state is clearly required.
- Coordinate contract changes with typed API boundaries instead of passing loosely typed payloads through props.

## Default Interaction Flow

1. Nuxt page, layout, or feature entry reads params and composes the workflow.
2. Composables, async-data utilities, or server helpers load or mutate server state.
3. Forms use explicit schema validation and composable or project-standard form wiring when user input is involved.
4. Presentation components render loading, empty, error, and success states with the existing design system.
5. Writes refresh, update, or invalidate the smallest correct data surface and show user feedback intentionally.
6. Tests cover the changed seam at composable, component, store, or flow level.

## Smells

- useFetch, useAsyncData, or $fetch calls inside leaf presentation components.
- Nuxt page files containing most of the feature logic.
- Untyped or loosely typed server payloads flowing through props.
- Validation duplicated between UI handlers and submit logic.
- Custom primitives replacing existing component-system pieces without a strong reason.
- Pinia stores used for request lifecycle problems or page-local state that fit composables or local state.

## Load Related Skills As Needed

- `frontend-feature` for end-to-end frontend delivery.
- `vue`, `nuxt`, `pinia`, `frontend-data-access`, `frontend-forms-and-validation`, `web-design-guidelines`, `api-contracts`, and `test-debug` based on the affected seam.

## Handoff

Return:
- target route, feature, or shared layer
- likely modules or folders affected
- composable, store, and data-loading notes
- form or contract changes
- risks around async state, reuse, or coupling
