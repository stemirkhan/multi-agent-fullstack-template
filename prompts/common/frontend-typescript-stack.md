Default frontend stack:
- Vue 3 with TypeScript
- `Nuxt 3` for app structure, routing, data loading, and server/client boundaries
- `Pinia` for shared client state when a composable is not enough
- composables for feature logic and reusable async workflows
- existing project design system before inventing new primitives
- schema-driven validation, using `Zod` or the project's established validation library

Architecture rules:
- Prefer existing project components and slots before building custom primitives.
- Keep data loading, writes, and API utilities in dedicated composables or Nuxt data seams.
- Keep page components thin and move reusable behavior into composables, stores, and shared components.
- Use strict typing across props, emits, API boundaries, and form schemas.
- Preserve accessibility, hydration safety, and responsive behavior when customizing components.

Avoid:
- putting $fetch, useFetch, or useAsyncData directly into presentational leaf components
- scattering validation rules across components, submit handlers, and stores
- using Pinia for page-local state that does not need cross-route coordination
