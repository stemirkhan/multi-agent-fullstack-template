---
name: frontend-feature
description: Use when implementing or modifying TypeScript React features with shadcn/ui components, typed API access, form handling, and frontend best practices.
---

# Frontend Feature

Use this skill as the top-level frontend orchestrator when a change spans components, data access, forms, and route-level behavior.

## Purpose

- Turn one frontend feature request into a coherent set of UI, state, and integration changes.
- Keep the implementation aligned with the stack contract: TypeScript-first React, `shadcn/ui`, `TanStack Query`, `React Hook Form`, and `Zod`.
- Decide which lower-level frontend skills are needed and in what order to apply them.

## Load Related Skills As Needed

- `frontend-typescript-react` for component, hook, and feature structure.
- `frontend-shadcn-ui` for reusable UI and accessible component composition.
- `frontend-data-access` for API clients, query hooks, cache invalidation, and mutation flows.
- `frontend-forms-and-validation` for forms, schemas, and backend error mapping.
- `api-contracts` when frontend contracts or generated clients change.
- `test-debug` when reproducing UI regressions or validating risky async behavior.

## Default Build Order

1. Clarify the user-facing workflow, route surface, async states, and acceptance criteria.
2. Identify affected contracts: props, query params, form schema, response shape, and API dependencies.
3. Decide whether the feature is mostly display, mostly form-driven, or mostly async state coordination.
4. Implement or update data-access hooks and client contracts first when server interaction is central.
5. Implement feature-level logic and component composition next.
6. Add or update forms and validation wiring where user input is involved.
7. Use existing `shadcn/ui` components before extending or creating new primitives.
8. Verify loading, empty, error, success, and responsive states.
9. Add or update tests at the right seam: hook, component, flow, or integration.

## Core Rules

- Start from the user workflow, not from isolated markup.
- Keep network access and mutation orchestration out of presentation-only leaves.
- Keep route and container code thin; push reusable behavior into hooks or feature modules.
- Prefer typed boundaries over loosely shaped objects and `any`.
- Preserve accessibility and interaction semantics when customizing component behavior.
- Reuse existing UI building blocks before creating new abstractions.

## Common Change Patterns

- New page or route:
  data access -> feature hook -> composed UI -> loading/error states -> tests
- New form:
  schema -> form wiring -> submit handler -> backend error mapping -> success state -> tests
- New async interaction:
  mutation hook -> invalidation/update strategy -> UI feedback -> tests
- Contract-driven change:
  API client -> query or mutation hook -> component props and rendering -> tests

## Definition Of Done

- Type boundaries are explicit.
- UI is built from existing component-system pieces where reasonable.
- Async states are handled coherently.
- Forms validate predictably and map backend failures clearly.
- Accessibility and responsive behavior are preserved.
- Tests cover the changed feature seam.

## Handoff

Return:
- routes or feature surfaces touched
- components introduced or extended
- query or mutation flows changed
- form and validation notes
- contract dependencies affected
- tests run
