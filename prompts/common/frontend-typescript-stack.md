Default frontend stack:
- React with TypeScript
- `shadcn/ui` for ready-made components
- `Radix UI` primitives
- `Tailwind CSS` styling
- `TanStack Query` for server state
- `React Hook Form` with `Zod` for forms and validation

Architecture rules:
- Prefer composing existing `shadcn/ui` components before building custom primitives.
- Keep server-state fetching and mutations in a dedicated data-access layer.
- Keep route and container code thin and move reusable UI into shared components.
- Use strict typing across props, API boundaries, and form schemas.
- Preserve accessibility and responsive behavior when customizing components.

Avoid:
- putting network logic directly into presentational leaf components
- scattering form validation rules across multiple layers
- inventing a custom UI kit when the existing component system is enough
