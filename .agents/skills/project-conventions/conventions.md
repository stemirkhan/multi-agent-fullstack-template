# Project Conventions

Use this file as the repo-local implementation reference that sits on top of
`stack/default-stack.yaml`.

## 1. General Rules

- Prefer explicit typed boundaries over loosely shaped dictionaries or `any`.
- Fail fast on invalid configuration or impossible states; do not hide them with speculative fallbacks.
- Reuse existing layers, components, and composables before adding new abstractions.
- Keep one clear source of truth for state, contracts, and validation rules.
- Update tests when public behavior, contracts, validation, or persistence behavior changes.

## 2. Backend Boundaries

- FastAPI controllers translate HTTP only and delegate use-case work to services.
- Services own orchestration, validation flow, and transaction entrypoints.
- Repositories encapsulate persistence details and do not call `commit()` themselves.
- Write flows go through an explicit Unit of Work so commit and rollback behavior stays testable.
- DTOs stay separate from ORM models and transport glue.
- Exceptions should be explicit and mapped intentionally at the HTTP boundary.
- Logging should be structured, useful for debugging, and free of secrets or noisy duplicate payloads.
- Dishka wiring should keep scopes and ownership obvious; avoid hidden lifecycle coupling.

## 3. Frontend Boundaries

- Treat Vue route views or screen-level entry components as thin composition surfaces.
- Put reusable behavior in composables before reaching for a store.
- Use Pinia only for shared client state that truly crosses features, screens, or durable user flows.
- Keep API access in typed clients, composables, or feature-level data-access modules, not in presentation leaves.
- Keep props, emits, and slot contracts narrow, typed, and intention-revealing.
- Prefer existing design-system components before inventing new primitives.
- Keep loading, empty, error, success, and disabled states explicit in UI flows.
- Make browser-only integrations, storage access, and environment-specific behavior explicit at the feature boundary.

## 4. Forms And Validation

- Use schema-driven validation, with one authoritative schema per form shape.
- Keep field naming, validation, and backend error mapping aligned.
- Do not duplicate the same validation logic across components, composables, and submit handlers.
- Keep submit side effects explicit: reset, redirect, invalidate, or preserve dirty state intentionally.
- Distinguish field-level feedback from form-level failures.

## 5. Contract Discipline

- When request or response shapes change, update both producer and consumer code in the same change when practical.
- Avoid silently reshaping backend payloads in components; normalize once at the data-access boundary.
- Preserve stable error semantics across backend services, controllers, and frontend consumers.
- Prefer explicit enums, typed objects, and named DTOs over magic strings and anonymous payloads.

## 6. Review And Testing Expectations

- Test the seam that changed, not just nearby files.
- For backend writes, cover commit and rollback behavior where risk is non-trivial.
- For API changes, cover response shape and error mapping.
- For frontend behavior, cover async states, accessibility-sensitive interactions, and validation flow when those seams change.
- If tests are not run, call that out explicitly as residual risk.

## 7. Common Smells

- Controllers talking to repositories directly.
- Services depending on FastAPI or HTTP primitives.
- Repositories creating their own session or committing independently.
- Components issuing raw network calls in render-heavy or presentation-only leaves.
- Pinia stores used for local component state or one-off request lifecycle state.
- Validation duplicated in multiple layers with conflicting messages.
- New abstractions that bypass an existing design-system or feature boundary without a clear reason.
