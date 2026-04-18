---
name: backend-feature
description: Use when implementing an end-to-end backend feature in the default Python stack, coordinating FastAPI controllers, services, DTOs, repositories, Unit of Work, exceptions, and logging.
---

# Backend Feature

Use this skill as the top-level backend orchestrator when a change spans multiple backend layers.

## Purpose

- Turn one backend feature request into a coherent set of layer changes.
- Keep the implementation aligned with the stack contract: thin FastAPI controllers, explicit services, Unit of Work transaction control, repositories, DTOs, exceptions, and structured logging.
- Decide which lower-level backend skills are needed and in what order to apply them.

## Load Related Skills As Needed

- `fastapi-controllers` when routes, request models, response models, or HTTP mapping change.
- `service-layer` when use-case logic changes.
- `backend-dtos` when data shapes cross transport or service boundaries.
- `unit-of-work` when the feature writes state or changes transaction behavior.
- `sqlalchemy-repositories` when persistence queries or save logic change.
- `backend-exceptions` when business or application failure semantics change.
- `backend-logging` when request, service, or failure observability changes.
- `dishka-di` when service or infrastructure wiring changes.
- `db-migration` when schema changes are required.
- `api-contracts` when OpenAPI or shared client-facing contracts change.
- `test-debug` when reproducing a bug or pinning down regression coverage.

## Default Build Order

1. Clarify the use case, input, output, invariants, and whether it is read-only or write-heavy.
2. Decide whether structural prep or family-port extraction must happen before behavior changes land.
3. Decide the transaction boundary and whether a Unit of Work is required.
4. Identify impacted contracts: request DTOs, response DTOs, service inputs, service outputs, and public API changes.
5. Implement or update the service layer first.
6. Add or adjust repository and Unit of Work behavior required by the service.
7. Apply DI wiring changes if new services, repositories, or gateways are introduced.
8. Add or update FastAPI controller code so the route only maps transport to the service and back.
9. Map exceptions and add meaningful structured logging at request, service, and failure boundaries.
10. Add or update tests at the appropriate level: service, repository, controller, and integration.

## Core Rules

- Start from the use case, not from the route handler.
- Keep controllers thin enough that the main body is effectively “parse, call service, map response”.
- Put business decisions in services, not in repositories or controllers.
- Keep writes behind an explicit Unit of Work.
- Keep service code dependent on abstract UoW or repository ports, not on concrete `SqlAlchemyUnitOfWork` construction.
- Do not land behavior against concrete infrastructure with a plan to abstract it later; extract the port first when boundary direction is changing.
- Keep repositories behind the service boundary and never call them directly from controllers.
- Keep DTOs and response contracts separate from ORM models.
- Make exception semantics explicit and map them at the HTTP boundary.
- Add logging for meaningful transitions and failures, not as line-by-line tracing.
- When the repo is docs-first, confirm the feature still matches the contract source of truth before changing runtime code.
- Keep product-code changes separate from agent-scaffolding changes unless the request explicitly couples them.

## Architectural Growth Guardrails

- Choose the landing zone before editing: controller, service, repository, DTO, model, or worker module.
- Prefer modules grouped by bounded context or use-case family over generic buckets such as one growing `auth.py` or `models.py`.
- If adding the change would introduce another distinct use-case family or bounded context into an already broad file, split first and then implement.
- If a change touches one cohesive subset of a broad UoW or repository surface, extract or reuse a family port before growing the broader surface further.
- When splitting a widely imported module, keep a compatibility facade until internal imports and callers have been migrated safely.
- If the change would push logic across controller, service, repository, or UoW seams, stop and split the work before editing.
- Mirror tests by domain from the start: for example `tests/api/auth/`, `tests/api/public/`, `tests/integration/<domain>/`.
- Treat “just append it to the existing big file” as a risk signal, not the default path.

## Read Versus Write Features

For read features:
- a service may orchestrate repository reads without a write transaction
- pagination, filtering, sorting, and response DTO shape matter most

For write features:
- define one clear Unit of Work boundary per use case
- validate before mutating
- commit explicitly
- ensure failure paths rollback cleanly

## Common Change Patterns

- New endpoint:
  service -> repository/UoW -> DTOs -> controller -> exceptions/logging -> tests
- New command or mutation:
  DTOs -> service -> UoW -> repositories -> controller mapping -> tests
- New query:
  repository -> service -> response DTO -> controller -> tests
- Cross-cutting change:
  start with service contract, then fan out to persistence, transport, and observability

## Definition Of Done

- Controller stays transport-focused.
- Service owns the use case logic.
- Repository and transaction boundaries are explicit.
- DI wiring matches the abstract interfaces used by services.
- DTO boundaries are clear.
- Exceptions are intentional and mapped.
- Logging is structured and useful.
- Write paths have rollback coverage, not just happy-path commit coverage.
- Boundary-refactor patches prove the intended narrow port, compatibility seam, and isolated test DB target when persistence is involved.
- Tests cover the changed behavior at the right seams.

## Handoff

Return:
- layers touched
- service entrypoints added or changed
- DTO and API contract changes
- transaction boundary notes
- DI, exception, and logging notes
- tests run
