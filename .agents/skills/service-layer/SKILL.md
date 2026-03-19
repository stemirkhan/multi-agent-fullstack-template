---
name: service-layer
description: Use when implementing application services, use-case orchestration, validation flow, transaction entrypoints, or service contracts for the Python backend.
---

# Service Layer

Use this skill when the change belongs to an application use case, not to HTTP transport or raw persistence.

## Responsibilities

- Accept already-parsed input via DTOs, command objects, or explicit typed arguments.
- Orchestrate business steps across repositories through a Unit of Work.
- Enforce application rules, sequencing, and cross-aggregate checks.
- Return DTOs or domain results, not framework objects.

## Keep Out

- FastAPI request parsing and response shaping.
- Direct SQLAlchemy session management.
- HTML, HTTP status, headers, cookies, or transport exceptions.
- Ad hoc logging everywhere; log at meaningful use-case boundaries.

## Default Shape

- Prefer one service class or module per use case group.
- Prefer explicit method names such as `create_user`, `cancel_order`, `assign_role`.
- Keep constructor dependencies narrow and typed.
- Inject repositories, policies, gateways, and the Unit of Work through Dishka.

## Workflow

1. Clarify the use case and the transaction boundary.
2. Define or update input and output DTOs if needed.
3. Read required state via repositories exposed by the Unit of Work.
4. Enforce business invariants and raise explicit application or domain exceptions.
5. Persist changes through repositories.
6. Commit or rollback through the Unit of Work.
7. Return a typed result for the controller or caller.

## Rules

- Open one explicit Unit of Work per write use case unless a higher-level boundary already exists.
- Keep side effects ordered: validate first, mutate second, publish or call integrations last.
- Avoid leaking ORM models outside the service boundary unless the project explicitly uses domain entities that wrap them.
- If several services need the same logic, extract a domain helper or policy instead of building a god-service.
- Prefer Pythonic code: small methods, explicit names, type hints, and obvious control flow.

## Testing

- Unit-test service logic against fake or test repositories where possible.
- Cover the happy path, invariant violations, and rollback-triggering failures.
- For write use cases, verify commit behavior explicitly.
- For read use cases, verify shape and typing of returned DTOs.

## Handoff

Return:
- changed service entrypoints
- DTO changes
- transaction boundary notes
- exceptions introduced or reused
- tests run
