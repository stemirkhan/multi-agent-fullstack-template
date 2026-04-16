Default frontend stack:
- Vue 3 with TypeScript
- route views or screen-level entry components for app structure and feature composition
- `Pinia` for shared client state when a composable is not enough
- composables for feature logic, data loading, and reusable async workflows
- existing project design system before inventing new primitives
- schema-driven validation, using `Zod` or the project's established validation library

Architecture rules:
- Prefer existing project components and slots before building custom primitives.
- Keep data loading, writes, and API utilities in dedicated composables or feature data-access modules.
- Keep route views and screen-level entry components thin and move reusable behavior into composables, stores, and shared components.
- Use strict typing across props, emits, API boundaries, and form schemas.
- Preserve accessibility, clear state ownership, and responsive behavior when customizing components.

Avoid:
- putting raw `fetch` or typed client calls directly into presentational leaf components
- scattering validation rules across components, submit handlers, and stores
- using Pinia for view-local state that does not need cross-feature coordination
