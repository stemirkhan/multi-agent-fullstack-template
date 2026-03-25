---
name: frontend-structure
description: Use when you need to understand or plan the default frontend structure in the TypeScript React stack, decide where UI, data access, and form logic belong, or map responsibilities across routes, feature modules, typed API access, validation, and shared components.
---

# Frontend Structure

Use this skill to orient work in the default frontend architecture before editing route code, feature modules, or shared UI.

## Purpose

- Map a frontend change to the correct feature, route, and shared-layer boundary.
- Keep changes aligned with `stack/default-stack.yaml`.
- Prevent route code, network logic, and presentation components from collapsing into one layer.

## Default Layer Map

- Route-level code: thin entry surfaces that read params, compose features, and own page-level states.
- `frontend-typescript-react`: feature structure, hooks, local state boundaries, and reusable React composition.
- `frontend-data-access`: typed API clients, `TanStack Query` hooks, mutations, and cache strategy.
- `frontend-forms-and-validation`: `React Hook Form`, `Zod`, submission flow, and backend error mapping.
- `frontend-shadcn-ui`: accessible UI primitives and composed components built from the existing kit.
- `api-contracts`: client-facing contract alignment when request or response shapes change.
- `test-debug`: regression isolation and validation for risky async or UI behavior.

## Placement Rules

- If the change is about page composition, routing params, or screen-level state, start at the route or feature container.
- If the change talks to the server, put the client and query or mutation logic in the data-access layer, not in leaf components.
- If the change collects user input, define schema and form wiring explicitly instead of scattering validation across handlers.
- If the change is visual, reuse `shadcn/ui` pieces before creating custom primitives.
- If logic is reused across multiple screens, extract it into a feature hook or shared component after the second clear use case.
- Keep local UI state near the feature; avoid broad client state stores unless cross-screen coordination is clearly required.
- Coordinate contract changes with typed API boundaries instead of passing loosely typed payloads through props.

## Default Interaction Flow

1. Route or feature container reads params and composes the workflow.
2. Data-access hooks load or mutate server state.
3. Forms use `Zod` schemas and `React Hook Form` wiring when user input is involved.
4. Presentation components render loading, empty, error, and success states with existing UI building blocks.
5. Mutations update or invalidate cache intentionally and surface user feedback.
6. Tests cover the changed seam at hook, component, or flow level.

## Smells

- Fetch or mutation calls inside leaf presentation components.
- Route files containing most of the feature logic.
- Untyped or loosely typed server payloads flowing through props.
- Validation duplicated between UI handlers and submit logic.
- Custom primitives replacing existing kit components without a strong reason.
- Global client state used for request lifecycle problems that fit query or local state.

## Load Related Skills As Needed

- `frontend-feature` for end-to-end frontend delivery.
- `frontend-typescript-react`, `frontend-data-access`, `frontend-forms-and-validation`, `frontend-shadcn-ui`, `api-contracts`, and `test-debug` based on the affected seam.

## Handoff

Return:
- target route, feature, or shared layer
- likely modules or folders affected
- data-access and cache notes
- form or contract changes
- risks around async state, reuse, or coupling
