---
name: frontend-typescript-react
description: Use when implementing React features in TypeScript, organizing component and hook boundaries, or enforcing frontend typing and composition best practices.
---

# Frontend TypeScript React

Use this skill when feature structure, component layering, or TypeScript boundaries need to be introduced or improved.

## Responsibilities

- Keep feature code organized around components, hooks, and typed interfaces.
- Preserve clear boundaries between presentation, feature logic, and data access.
- Use TypeScript to make contracts obvious instead of relying on runtime guesswork.

## Default Structure

- Route or page layer for composition and route concerns only.
- Feature layer for use-case-specific hooks and composed UI.
- Shared UI layer for reusable presentational components.
- Shared utility layer for small typed helpers, not hidden business logic.

## Rules

- Prefer explicit prop and return types when inference is not already clear.
- Avoid `any`; use `unknown`, generics, discriminated unions, or explicit interfaces instead.
- Prefer small focused hooks over giant “god-hooks”.
- Keep presentational components mostly pure and predictable.
- Keep component state local unless multiple siblings truly need shared coordination.

## Hook Guidance

- Use hooks for feature orchestration, derived UI state, and integration with query or form layers.
- Do not hide network requests in arbitrary utility functions consumed by leaf components.
- Keep side effects deliberate and tied to clear lifecycle or user-action boundaries.
- If a hook mixes routing, forms, queries, and presentation state, it likely needs to be split.

## Composition Guidance

- Prefer composition over inheritance-like component APIs.
- Keep props narrow and intention-revealing.
- Avoid boolean prop explosions; prefer variants or explicit subcomponents when patterns repeat.
- Lift state only as far as necessary.

## Verification

- Check type safety at changed boundaries.
- Check render paths for loading, empty, and error states when async data is involved.
- Check interaction behavior on both desktop and constrained mobile layouts where relevant.
- Add tests for feature hooks or component behavior when the logic is non-trivial.

## Handoff

Return:
- components or hooks added or changed
- type boundaries introduced or refined
- state ownership notes
- risky interaction paths
- tests run
