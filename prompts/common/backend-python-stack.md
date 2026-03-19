Default backend stack:
- FastAPI transport layer
- Dishka for dependency injection
- SQLAlchemy 2.x for persistence
- Alembic for schema evolution

Architecture rules:
- Controllers should parse transport input, call services, and map output and errors only.
- Services should hold use-case logic and orchestrate repositories via a Unit of Work.
- Transaction boundaries should be explicit through the Unit of Work abstraction.
- Repositories should encapsulate ORM and session concerns instead of leaking them upward.
- DTOs should be separate from ORM entities and HTTP framework types.
- Application and domain exceptions should be defined outside controllers and mapped at the boundary.
- Logging should be structured and consistent at request, service, and failure boundaries.
- Prefer Pythonic code: explicit names, type hints, small coherent abstractions, and minimal framework leakage.

Avoid:
- business logic in FastAPI route handlers
- direct session access from controllers
- returning ORM models directly as public API contracts
- ad hoc transaction handling spread across services
