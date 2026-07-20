---
name: service-layer
description: Use when implementing application services, use-case orchestration, validation flow, transaction entrypoints, or service contracts for the Python backend.
---

# Service Layer

Use this skill when the change belongs to an application use case, not to HTTP transport or raw persistence.

## Responsibilities

- Accept already-parsed input via DTOs, command objects, or explicit typed arguments.
- Orchestrate business steps through narrow application ports; coordinate write repositories through a Unit of Work.
- Enforce application rules, sequencing, and cross-aggregate checks.
- Return DTOs or domain results, not framework objects.

## Keep Out

- FastAPI request parsing and response shaping.
- Direct SQLAlchemy session management.
- Concrete `SqlAlchemyUnitOfWork` or `AsyncSession` construction.
- HTML, HTTP status, headers, cookies, or transport exceptions.
- Ad hoc logging everywhere; log at meaningful use-case boundaries.

## Default Shape

- Prefer one service class or module per use case group.
- Choose the landing zone before editing and decide whether structural prep is required before behavior changes.
- Prefer explicit method names such as `create_user`, `cancel_order`, `assign_role`.
- Keep constructor dependencies narrow and typed.
- Inject reader, writer/UoW, policy, and gateway ports through Dishka.
- If one file starts mixing unrelated flows such as registration, sessions, recovery, and profile reads, split by use-case family before adding more logic.
- Put shared helpers in a nearby `common.py` or policy/helper module instead of keeping everything in one growing service file.

## Workflow

1. Clarify the use case and the transaction boundary.
2. Define or update input and output DTOs if needed.
3. Read required state through the narrow reader port or the transactional writer repository appropriate to the invariant.
4. Enforce business invariants and raise explicit application or domain exceptions.
5. Persist changes through repositories.
6. Commit or rollback through the Unit of Work.
7. Return a typed result for the controller or caller.

## Rules

- Open one explicit Unit of Work per write use case unless a higher-level boundary already exists.
- Depend on abstract UoW or repository ports in service constructors; concrete session or UoW setup belongs in infrastructure and DI.
- Application services must not import `infrastructure`, `di`, `AsyncSession`, concrete repositories, or concrete UoW implementations.
- Keep reader, writer, provider, and policy ports separate when their capabilities or lifecycle differ.
- If an unplanned second capability family appears, pause that branch and extract a narrow port or landing zone before adding its behavior; normal planned end-to-end layer work may continue.
- Keep side effects ordered: validate first, mutate second, publish or call integrations last.
- Keep I/O async; isolate unavoidable blocking providers behind explicit adapters.
- Avoid leaking ORM models outside the service boundary unless the project explicitly uses domain entities that wrap them.
- When a write flow returns a rich DTO, prefer final projection through a reader port or dedicated query seam instead of widening the mutation port with read-model assembly.
- If several services need the same logic, extract a domain helper or policy instead of building a god-service.
- Prefer Pythonic code: small methods, explicit names, type hints, and obvious control flow.
- When refactoring a widely imported service module, preserve a temporary compatibility facade so callers can migrate without a large risky patch.

## Testing

- Unit-test service logic against fake or test application ports where possible.
- Prefer fake or test UoWs over concrete infrastructure UoWs in service-level tests.
- Cover the happy path, invariant violations, and rollback-triggering failures.
- For write use cases, verify commit behavior explicitly.
- For failing write paths, assert rollback through the abstract UoW surface.
- For read use cases, verify shape and typing of returned DTOs.
- For boundary refactors, add a focused seam test proving the service now depends on the intended abstract family port rather than a broader legacy surface or infrastructure type.

## Example

```python
# application/services/create_user.py
from dataclasses import dataclass
from application.dtos.users import CreateUserDTO, UserDTO
from application.exceptions import UserAlreadyExistsError
from application.ports.users import UserWriteUnitOfWork

@dataclass
class CreateUser:
    uow: UserWriteUnitOfWork

    async def execute(self, cmd: CreateUserDTO) -> UserDTO:
        async with self.uow:
            if await self.uow.users.email_exists(cmd.email):
                raise UserAlreadyExistsError(email=cmd.email)
            user = await self.uow.users.add(email=cmd.email, name=cmd.name)
            result = UserDTO(id=user.id, email=user.email, name=user.name)
            await self.uow.commit()
            return result
```

Key points: the service imports only application contracts, `async with` delegates a real transaction lifecycle to the concrete UoW, commit is explicit, and no ORM model crosses the service boundary. If the result needs joins or a rich read model, use a dedicated reader/query port with explicit consistency semantics instead of expanding the writer.

## Handoff

Return:
- changed service entrypoints
- DTO changes
- transaction boundary notes
- exceptions introduced or reused
- tests run
