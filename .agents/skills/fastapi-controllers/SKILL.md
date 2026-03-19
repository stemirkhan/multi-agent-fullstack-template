---
name: fastapi-controllers
description: Use when implementing or updating FastAPI route handlers, dependency wiring at the HTTP boundary, request and response mapping, and controller-level error translation.
---

# FastAPI Controllers

Use this skill when work touches route handlers, routers, request and response models, or transport-level exception mapping.

## Responsibilities

- Define HTTP routes, methods, status codes, and tags.
- Parse incoming request data into typed transport models.
- Resolve service dependencies through Dishka-integrated injection.
- Call one service entrypoint per use case path.
- Map service results and known exceptions into HTTP responses.

## Keep Thin

- No business logic in route handlers.
- No direct repository usage from controllers.
- No direct session lifecycle management.
- No duplicated validation that already belongs in DTOs or services.

## Default Flow

1. Receive request via FastAPI model, path params, query params, or headers.
2. Convert transport input into the service input shape when needed.
3. Call the service.
4. Map the result to a response DTO.
5. Translate known application exceptions into stable HTTP responses.

## Error Mapping

- Prefer central exception handlers for shared application and domain exceptions.
- Keep per-route error handling minimal and only for route-specific concerns.
- Do not leak raw SQLAlchemy errors or tracebacks in public responses.
- Preserve error semantics: validation, not found, conflict, forbidden, and unexpected failures should stay distinguishable.

## Dependency Injection

- Prefer injecting services, not lower layers, into controllers.
- Keep dependency signatures explicit and typed.
- If multiple routes need the same dependency bundle, factor it into router-level composition or provider wiring, not copy-paste.

## Response Rules

- Return response DTOs or explicit FastAPI response objects only when transport control is required.
- Avoid returning ORM models directly.
- Keep pagination, filtering, and metadata shapes consistent across endpoints.

## Testing

- Test route status codes, response shapes, and exception mapping.
- Mock or override services at the dependency boundary when unit-testing controllers.
- Add integration coverage for critical routes where DI, auth, and serialization meet.

## Handoff

Return:
- routes added or changed
- request and response DTO changes
- injected services
- HTTP error mapping notes
- tests run
