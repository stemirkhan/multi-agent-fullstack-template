---
name: backend-structure
description: Use when you need to understand or plan the default backend structure in the Python stack, decide where a change belongs, or map responsibilities across FastAPI controllers, services, DTOs, Unit of Work, repositories, exceptions, and logging.
---

# Backend Structure

Use this skill to orient work in the default backend architecture before editing code or creating new backend modules.

## Purpose

- Map a backend change to the correct layer and ownership boundary.
- Keep changes aligned with `stack/default-stack.yaml`.
- Prevent controller, service, and repository responsibilities from drifting together.

## Default Layer Map

- `fastapi-controllers`: HTTP-only transport. Parse requests, call services, map responses and errors.
- `service-layer`: use-case orchestration, business decisions, validation order, and coordination.
- `backend-dtos`: explicit request, response, command, and query contracts across boundaries.
- `unit-of-work`: transaction boundary for write use cases.
- `sqlalchemy-repositories`: persistence access hidden behind repository abstractions.
- `backend-exceptions`: explicit application and domain failures.
- `backend-logging`: structured logs around requests, use cases, and failures.
- `dishka-di`: dependency wiring across application and infrastructure layers.
- `db-migration`: schema changes required to support behavior changes.

## Placement Rules

- If the change is about HTTP shape, status codes, or request parsing, start at the controller boundary.
- If the change is about business behavior, invariants, or orchestration, start in the service layer.
- If data crosses a layer boundary, prefer an explicit DTO instead of ad hoc dicts or ORM objects.
- If state changes, define or confirm the Unit of Work boundary before wiring persistence.
- If new queries or persistence operations are needed, add them in repositories, not in controllers.
- If a new failure mode matters to callers, model it as an explicit exception and map it at the HTTP boundary.
- If new infrastructure objects are introduced, wire them through Dishka instead of constructing them inline.

## Default Request Flow

1. Controller receives HTTP input and maps it to service inputs or DTOs.
2. Service validates rules and orchestrates the use case.
3. Service uses Unit of Work for writes and repositories for persistence.
4. Service returns DTOs or raises explicit exceptions.
5. Controller maps the result to HTTP and translates failures.
6. Logging records important transitions and failures.

## Smells

- Controllers calling repositories directly.
- Services returning ORM models to outer layers.
- Repositories owning business rules.
- Hidden transaction boundaries or implicit commits.
- Unstructured dicts crossing module boundaries.
- Catch-all exceptions without domain meaning.

## Load Related Skills As Needed

- `backend-feature` for end-to-end backend delivery.
- `fastapi-controllers`, `service-layer`, `backend-dtos`, `unit-of-work`, `sqlalchemy-repositories`, `backend-exceptions`, `backend-logging`, `dishka-di`, `db-migration`, `api-contracts`, and `test-debug` based on the affected layers.

## Handoff

Return:
- target layer or layers
- likely modules or folders affected
- transaction notes
- contract changes
- risks or coupling to watch
