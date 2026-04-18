---
name: sqlalchemy-repositories
description: Use when implementing repository abstractions, SQLAlchemy 2.x queries, persistence mapping, or data access patterns hidden behind repository interfaces.
---

# SQLAlchemy Repositories

Use this skill when persistence logic belongs in a repository instead of in services or controllers.

## Responsibilities

- Encapsulate SQLAlchemy queries, persistence operations, and loading strategies.
- Present stable methods to the service layer in domain or use-case terms.
- Keep session-bound persistence details out of services.
- Support transaction participation through the Unit of Work.

## Keep In Repositories

- Filtering, loading, and query composition.
- `select`, `insert`, `update`, `delete`, and flush behavior tied to persistence.
- ORM-specific optimizations such as eager loading or bulk operations when justified.

## Keep Out

- HTTP concerns.
- Cross-use-case business orchestration.
- Ad hoc transaction commits.
- Presentation-specific DTO formatting.

## Method Design

- Prefer business-meaningful methods such as `get_by_email`, `list_active_for_account`, `save`, `delete`.
- Avoid generic “query builder” repositories that just expose the session indirectly.
- Return a consistent shape: ORM entities, domain entities, or persistence models, depending on project choice.
- Keep pagination and filtering contracts explicit.
- Group repositories and persistence models by bounded context or query family, not by one ever-growing infrastructure file.
- If a repository file begins to mix unrelated read models or write concerns, split it before adding another query family.
- If a service only needs one cohesive capability family, expose or depend on a family-specific repository port instead of extending a broad catch-all repository surface.

## Query Rules

- Default to SQLAlchemy 2.x style queries.
- Use eager loading deliberately to prevent N+1 issues on known access paths.
- Keep query complexity readable; extract helpers when predicates or joins become non-trivial.
- Do not hide expensive collection loading behind innocent-looking methods.

## Session Rules

- Receive the session from the Unit of Work or provider wiring.
- Do not create a fresh session inside repository methods.
- Do not call `commit()` from repositories.
- Use `flush()` only when the use case needs identifiers or database-side effects before commit.
- When reorganizing widely used model imports, prefer an internal package plus a stable facade rather than a breaking import rename across the whole repo.

## Testing

- Cover representative queries with integration tests against a real test database when possible.
- Show the effective test DB target for integration verification; do not treat dev, shared app, or inherited non-test DB settings as acceptable persistence coverage.
- Verify loading behavior for critical hot paths.
- Test not-found, conflict, and filtering edge cases.
- For repository or UoW surface refactors, add at least one integration test proving the narrow port still participates in the same real transaction.
- Keep repository tests focused on persistence behavior, not service orchestration.

## Example

```python
# repositories/user_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def add(self, email: str, name: str) -> User:
        user = User(email=email, name=name)
        self._session.add(user)
        await self._session.flush()  # get id before commit
        return user
```

Key points: session is injected, never created here; `commit()` is absent; `flush()` used only to get the generated id before the transaction closes.

## Handoff

Return:
- repositories added or changed
- query and loading strategy notes
- entity or model shapes returned
- flush assumptions
- tests run
