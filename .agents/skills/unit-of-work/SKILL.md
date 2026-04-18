---
name: unit-of-work
description: Use when defining or applying Unit of Work abstractions for transaction management, commit and rollback behavior, and service-to-repository coordination.
---

# Unit Of Work

Use this skill when transaction boundaries need to be introduced, changed, or verified.

## Responsibilities

- Provide a single transaction boundary for one application use case.
- Expose repositories participating in that transaction.
- Centralize `commit`, `rollback`, and lifecycle control.
- Hide direct session handling from services and controllers.

## Default Shape

- Prefer an interface such as `AbstractUnitOfWork`.
- Expose repositories as attributes or typed accessors on the UoW.
- If one shared UoW attribute starts serving multiple capability families, extract narrower family ports or aliases before another use case lands on the broad surface.
- Support `async with uow:` when the stack is async.
- Keep `commit()` explicit for write flows; do not silently commit on object mutation.

## Rules

- Controllers should not create or manage sessions directly.
- Services should coordinate repositories through the UoW, not around it.
- Only the composition root, DI provider, or dedicated factory should construct a concrete `SqlAlchemyUnitOfWork`.
- Treat `SqlAlchemyUnitOfWork(...)` or raw `AsyncSession` creation inside service code as a boundary violation.
- Treat shared UoW surface growth as a refactor trigger. If a change needs one cohesive subset of a broad UoW attribute, extract or use a family-specific port first.
- One request may contain multiple read operations, but write consistency should still map to a clear use-case boundary.
- Nested Unit of Work patterns are usually a smell; prefer one top-level boundary per use case.
- If a service needs partial failure handling, design it explicitly instead of committing incrementally.

## Repository Access

- Repositories that share one transaction should be obtained from the same UoW instance.
- Do not construct repositories ad hoc with fresh sessions inside service methods.
- Keep repository naming stable and predictable, for example `uow.users`, `uow.orders`.

## Failure Behavior

- On any exception before commit, rollback the transaction.
- Map low-level database failures into explicit application errors at the appropriate boundary.
- Log failures with enough context to diagnose the use case, but avoid leaking secrets or raw payloads.

## Testing

- Verify commit is called on successful write flows.
- Verify rollback is triggered on failing write flows.
- Verify repositories accessed inside one UoW share the same transactional context.
- Verify the abstract UoW or UoW factory is the interface consumed by services.
- Verify newly introduced family aliases on the concrete UoW preserve the same session and `async with` lifecycle as the broader implementation.
- Verify refactored services use the narrow UoW port or alias instead of the legacy broad attribute when a split is introduced.
- Verify provider or factory wiring preserves `async with` lifecycle and rollback semantics through the abstract interface.
- Include at least one integration test for critical transactional invariants.

## Example

```python
# uow.py
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, OrderRepository

class AbstractUnitOfWork(ABC):
    users: UserRepository
    orders: OrderRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    async def __aexit__(self, *exc) -> None:
        if exc[0]:
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.users = UserRepository(session)
        self.orders = OrderRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
```

Key points: repositories share the same session, `commit()` is always explicit, `__aexit__` rolls back on exception automatically.

## Handoff

Return:
- UoW interface or implementation changes
- factory or DI wiring notes
- repositories attached to the UoW
- commit and rollback semantics
- tests proving transactional behavior
