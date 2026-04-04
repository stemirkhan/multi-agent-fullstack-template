---
name: pinia
description: Use when implementing shared client state, store actions, derived state, or store-boundary decisions in the Vue and Nuxt frontend.
---

# Pinia

Use this skill when state must outlive one component or coordinate behavior across pages or features.

## Responsibilities

- Keep shared state intentional and well-bounded.
- Use stores for cross-route or multi-feature coordination, not page-local transient state.
- Keep actions, derived state, and transport boundaries explicit.

## Rules

- Prefer local state or composables before reaching for a store.
- Keep stores cohesive around one ownership boundary.
- Do not hide raw API calls throughout unrelated stores without clear reasoning.
- Keep optimistic updates, refresh behavior, and rollback semantics explicit.
- Type state, getters, and action inputs deliberately.

## Verification

- Check state initialization, refresh, and reset behavior.
- Check action failure and rollback paths.
- Check whether a store is truly needed versus a composable.

## Handoff

Return:
- stores or actions added or changed
- shared state boundaries introduced or refined
- refresh or rollback notes
- tests run
