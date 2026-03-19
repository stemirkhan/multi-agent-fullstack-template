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
- Support `async with uow:` when the stack is async.
- Keep `commit()` explicit for write flows; do not silently commit on object mutation.

## Rules

- Controllers should not create or manage sessions directly.
- Services should coordinate repositories through the UoW, not around it.
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
- Include at least one integration test for critical transactional invariants.

## Handoff

Return:
- UoW interface or implementation changes
- repositories attached to the UoW
- commit and rollback semantics
- tests proving transactional behavior
