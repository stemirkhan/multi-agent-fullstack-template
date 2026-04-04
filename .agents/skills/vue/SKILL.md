---
name: vue
description: Use when implementing Vue 3 components, props and emits contracts, slots, composables, and TypeScript-first Composition API patterns.
---

# Vue

Use this skill for Vue 3 component and composable work in the default frontend stack.

## Responsibilities

- Prefer Composition API with clear props, emits, and slot boundaries.
- Keep reusable logic in composables, not hidden in giant page components.
- Preserve strong TypeScript typing at component and composable seams.

## Rules

- Keep props narrow and intention-revealing.
- Prefer computed state and composables over deeply nested watchers.
- Keep side effects explicit and tied to lifecycle or user action boundaries.
- Use slots and composition before growing large option surfaces.
- Avoid broad shared state when local component state or a composable is enough.

## Verification

- Check changed props, emits, and slot contracts.
- Check component behavior on loading, empty, error, and success states when async data is involved.
- Add tests for non-trivial composables or component interactions.

## Handoff

Return:
- components or composables added or changed
- prop, emit, or slot boundaries touched
- state ownership notes
- tests run
