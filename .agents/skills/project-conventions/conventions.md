# Project Conventions

Use this file as the implementation reference derived from
`stack/default-stack.yaml`. The stack contract is authoritative; update it first
when a default architecture or capability changes.

## 1. General Rules

- Prefer explicit typed boundaries over loosely shaped dictionaries or `any`.
- Treat the stack runtime as a baseline; each target project declares and tests a finite supported minor range and owns its dependency pins.
- Fail fast on invalid configuration or impossible states; do not hide them with speculative fallbacks.
- Reuse existing layers, components, and composables before adding new abstractions.
- Choose the intended landing zone before editing.
- If a change requires a new dependency family, port, or module boundary, complete structural prep before feature behavior.
- A planned end-to-end change may span layers. Pause only for unplanned boundary widening, a wrong landing zone, or conflicting ownership.
- Keep one clear source of truth for state, contracts, configuration, and validation rules.

## 2. Backend Boundaries

- Keep I/O paths async from FastAPI through services, repositories, and Unit of Work; isolate blocking adapters from the event loop.
- FastAPI controllers translate HTTP only and delegate use-case work to services.
- Services own orchestration and depend on application ports, never infrastructure implementations, ORM models, DI wiring, or framework adapters.
- Keep application ports narrow by capability. Split reader, writer, provider, and policy seams when responsibilities diverge.
- Keep rich result projection on a reader or query seam rather than widening a mutation port.
- Repositories encapsulate persistence details, receive their session from the UoW or provider, and never call `commit()`.
- Write flows use an explicit Unit of Work with truthful async entry, explicit commit, and rollback/cleanup on exit.
- DTOs stay separate from ORM models and transport glue.
- Use Pydantic v2 models for typed transport DTOs and settings; keep business invariants in the application or domain layer.
- Raise explicit application or domain exceptions and map them intentionally at the HTTP boundary.
- Dishka providers make scope, resource ownership, and lifecycle explicit.

## 3. Frontend Boundaries And State

- Treat Vue route views and screen-level components as thin composition surfaces.
- Put reusable behavior in composables before reaching for a store.
- Keep server state, request status, refresh, and invalidation in typed data-access or query seams.
- Use Pinia only for shared client-owned state that crosses features, routes, or durable user flows.
- Keep transient presentation and form state local; do not mirror server state into Pinia without an explicit synchronization policy.
- Keep API access in typed clients, composables, or feature-level data-access modules, not presentation leaves.
- Keep props, emits, slots, and composable contracts narrow, typed, and intention-revealing.
- Prefer existing design-system components before inventing new primitives.
- Keep loading, empty, error, success, disabled, retry, and optimistic-rollback states explicit where relevant.
- Make browser-only integrations, storage access, and environment-specific behavior explicit at the feature boundary.

## 4. Forms And Validation

- Use one authoritative schema per form shape and the project's established schema library.
- Keep field naming, validation, and backend error mapping aligned.
- Keep transport validation at the boundary and business validation in services; do not duplicate either across layers.
- Distinguish field-level feedback from form-level, authorization, and conflict failures.
- Keep submit side effects explicit: reset, redirect, invalidate, or preserve dirty state intentionally.
- Guard duplicate submission and preserve user input on recoverable failures.

## 5. API Contract Discipline

- Treat emitted FastAPI OpenAPI, derived from explicit DTO, route, status, header, authentication, and documented error declarations, as the public API definition.
- Treat request, response, route, status, header, authentication, error, pagination, enum, default, and nullability changes as contract changes.
- Prefer additive evolution; document the migration path and coexistence window for breaking changes.
- Update producers, generated or handwritten TypeScript clients, and consumers in the same workstream when practical.
- When generation is used, regenerate artifacts and keep a CI drift check.
- Normalize payloads once at the data-access boundary instead of silently reshaping them in components.

## 6. Security And Observability

- Enforce authentication and authorization on the backend; UI restrictions are not security controls.
- Validate untrusted input and render untrusted content safely.
- Keep secrets, credentials, tokens, raw sensitive payloads, and private error details out of logs and telemetry.
- Configure cookies, storage, CORS, CSRF defenses, and trusted proxies deliberately for the deployment model.
- Use structured backend logs and propagate request or trace correlation through async boundaries where available.
- Instrument meaningful request, use-case, dependency, and client-failure seams without noisy duplicate telemetry.
- Separate user-facing frontend feedback from diagnostic telemetry while preserving machine-readable error semantics.

## 7. Review And Testing Expectations

- Test the seam that changed, not just nearby files.
- Unit-test services against fake application ports; integration-test repositories, UoW, DI, and migrations against real isolated persistence.
- Persistence tests must use a dedicated test database or isolated transaction scope and fail fast if configuration points at a dev, shared, or production-like target.
- For backend writes, cover explicit commit, rollback, and async resource lifecycle where risk is material.
- For API changes, cover serialization, response shape, stable error mapping, and affected consumers.
- For frontend behavior, cover state ownership, refresh/invalidation, async states, validation, accessibility-sensitive interactions, and duplicate submission as relevant.
- Use browser automation only when it is installed and a real browser flow is the smallest reliable verification seam.
- If tests are not run, call that out explicitly as residual risk.

## 8. Common Smells

- Controllers talking to repositories or sessions directly.
- Application code importing `infrastructure`, concrete UoWs or repositories, ORM models, DI modules, or framework adapters.
- One broad port mixing unrelated capability families or read projections with mutation concerns.
- Repositories creating sessions or committing independently.
- An abstract UoW that claims to open a transaction while only returning `self`.
- Components issuing raw network calls in render-heavy or presentation-only leaves.
- Pinia stores used as a second server cache or for local component state.
- Validation duplicated across components, composables, and submit handlers.
- Persistence tests whose effective database target is unknown or shared.
- Feature logic appended before required landing-zone or boundary preparation.
