---
name: unit-of-work
description: Use when defining or applying Unit of Work abstractions for transaction management, commit and rollback behavior, and service-to-repository coordination.
---

# Unit Of Work

Use this skill when transaction boundaries need to be introduced, changed, or verified.

## Responsibilities

- Provide one transaction boundary for one write use case.
- Expose the narrow writer repositories participating in that transaction.
- Centralize explicit `commit`, rollback, and async resource lifecycle control.
- Keep SQLAlchemy sessions and concrete repositories out of application services and controllers.

## Application Port

- Define UoW and repository protocols in the application layer without SQLAlchemy imports.
- Keep port families capability-oriented; do not grow one catch-all UoW for unrelated domains.
- Separate reader/query ports from writer/UoW ports unless a read must share the write transaction for an invariant.
- Keep rich result projection on a reader seam instead of adding presentation queries to a mutation port.

## Infrastructure Adapter

- Implement the application port in infrastructure and construct it only in DI or the composition root.
- Make resource ownership explicit: whichever layer creates a session must close it.
- In the async default, `__aenter__` starts the real transaction and initializes repositories on that session.
- Keep commit explicit. On exit, roll back any still-active transaction and release owned resources.
- Do not claim that an abstract `__aenter__` returning `self` opens a transaction.

## Rules

- Controllers do not create sessions or UoW instances.
- Services depend on application ports, never `AsyncSession`, concrete repositories, or concrete UoWs.
- Repositories in one transaction come from the same UoW and never commit independently.
- A read-only use case may use a dedicated reader port without a write UoW.
- Avoid nested UoWs and incremental commits; design partial failure and post-commit effects explicitly.
- If a broad UoW gains an unplanned second capability family, extract a family port before adding that behavior. Planned end-to-end work may implement its port and adapter together.

## Failure Behavior

- If a context exits before successful explicit commit, roll back the active transaction.
- Map low-level database failures into explicit application errors at the chosen boundary.
- Retry a whole transaction only when idempotency and retryable failures are understood.
- Log enough failure context to diagnose the use case without secrets or sensitive payloads.

## Testing

- Verify explicit commit on success and rollback on exceptions or missing commit.
- Verify repositories from one UoW share the same session and transaction.
- Verify services consume the abstract family port.
- Verify DI/factory wiring preserves `async with`, commit, rollback, and cleanup behavior.
- Run critical transaction tests against an isolated test database or transaction scope that fails fast on dev or shared targets.

## Lifecycle Sketch

```python
# Application port: no SQLAlchemy imports.
class UserWriteUnitOfWork(Protocol):
    users: UserWriter
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *exc: object) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

Read [the complete async SQLAlchemy example](references/async-sqlalchemy-example.md)
before implementing an adapter. It includes typed ports, enter-failure cleanup,
deterministic rollback, and session ownership variants.

## Handoff

Return:
- application UoW and repository ports changed
- concrete adapter and DI ownership notes
- repositories attached to the transaction
- commit, rollback, and cleanup semantics
- isolated persistence tests run
