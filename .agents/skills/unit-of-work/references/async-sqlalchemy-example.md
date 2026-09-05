# Async SQLAlchemy Unit Of Work Example

Use this reference when a concrete implementation is needed. The example uses
a session factory, so the Unit of Work owns both the session and its cleanup.

## Application Ports

The application contract contains no persistence implementation types:

```python
# application/ports/users.py
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Protocol, Self

from domain.users import User


class UserWriter(Protocol):
    async def email_exists(self, email: str) -> bool: ...
    async def add(self, *, email: str, name: str) -> User: ...


class UserWriteUnitOfWork(ABC):
    users: UserWriter

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
```

## Infrastructure Adapter

The adapter starts a real transaction on entry, rolls back any transaction
left active on exit, and closes the session it created:

```python
# infrastructure/persistence/uow.py
from types import TracebackType

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncSessionTransaction,
    async_sessionmaker,
)

from application.ports.users import UserWriteUnitOfWork
from infrastructure.persistence.users import SqlAlchemyUserWriter


class SqlAlchemyUserWriteUnitOfWork(UserWriteUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._transaction: AsyncSessionTransaction | None = None

    async def __aenter__(self) -> "SqlAlchemyUserWriteUnitOfWork":
        if self._session is not None:
            raise RuntimeError("Unit of Work is already active")
        session = self._session_factory()
        transaction: AsyncSessionTransaction | None = None
        try:
            transaction = await session.begin()
            users = SqlAlchemyUserWriter(session)
        except BaseException:
            try:
                if transaction is not None and transaction.is_active:
                    await transaction.rollback()
            finally:
                await session.close()
            raise
        self._session = session
        self._transaction = transaction
        self.users = users
        return self

    async def commit(self) -> None:
        await self._active_transaction().commit()

    async def rollback(self) -> None:
        transaction = self._active_transaction()
        if transaction.is_active:
            await transaction.rollback()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if self._transaction is not None and self._transaction.is_active:
                await self._transaction.rollback()
        finally:
            if self._session is not None:
                await self._session.close()
            self._transaction = None
            self._session = None

    def _active_transaction(self) -> AsyncSessionTransaction:
        if self._transaction is None:
            raise RuntimeError("Unit of Work is not active")
        return self._transaction
```

## Ownership Variant

If Dishka owns a request-scoped session instead, the concrete UoW should not
close a resource owned by the provider. It must still start a real transaction,
commit only when asked, and deterministically roll back an active transaction
on context exit. Document that ownership in the provider and cover it through
the abstract port used by the service.
