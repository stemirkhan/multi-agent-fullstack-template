---
name: dishka-di
description: Use when wiring application dependencies with Dishka providers, scopes, factories, FastAPI integration, or runtime composition rules.
---

# Dishka DI

Use this skill when dependencies, provider layout, scopes, or composition roots need to be introduced or changed.

## Responsibilities

- Define how services, repositories, Unit of Work implementations, gateways, and configs are constructed.
- Keep composition at the boundary instead of scattering factory logic across feature modules.
- Align lifetimes with request, app, and transactional scopes.
- Integrate the container cleanly with FastAPI.

## Default Layout

- Keep providers near the composition root or in a dedicated `di/` package.
- Group providers by concern: config, infrastructure, persistence, application services, transport wiring.
- Prefer explicit provider functions over magic or dynamic container assembly.
- Keep interfaces and implementations easy to trace from provider to consumer.

## Rules

- Controllers should depend on services, not repositories or sessions, unless the route is deliberately infra-oriented.
- Services should receive fully constructed dependencies from Dishka, not assemble them manually.
- Repositories and Unit of Work implementations should be wired once in providers, not ad hoc in business code.
- Prefer typed constructor injection and explicit provider return types.
- Avoid circular dependency graphs; if they appear, the design likely needs to be split.

## Scope Guidance

- App scope for stable infrastructure such as config, logger factories, and long-lived clients.
- Request scope for request-bound services and per-request contextual dependencies.
- Transaction or operation scope for Unit of Work and session-backed persistence objects when the project uses them separately.
- Be conservative with singleton-like objects that carry mutable state.

## FastAPI Integration

- Compose the Dishka container in app startup code or the main app factory.
- Use framework integration to inject service dependencies into route handlers.
- Keep DI glue in transport setup, not inside route functions.
- If auth, request context, or correlation IDs are injected, ensure their scope matches the request lifecycle.

## Testing

- Override providers at the container boundary instead of monkey-patching deep call sites.
- Use test containers or provider overrides for fakes, stubs, and isolated service tests.
- Verify that request-scoped objects are not accidentally reused across tests or requests.
- Keep a small integration test proving FastAPI and Dishka wiring works end to end.

## Handoff

Return:
- providers added or changed
- scopes and lifecycle choices
- FastAPI integration points touched
- test override strategy
- tests run
