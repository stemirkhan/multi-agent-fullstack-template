---
name: backend-exceptions
description: Use when defining domain or application exceptions, translating them at the FastAPI boundary, or keeping error semantics consistent across services.
---

# Backend Exceptions

Use this skill when error semantics need to be made explicit instead of relying on generic runtime failures.

## Responsibilities

- Define meaningful domain and application exceptions.
- Keep service-level failure semantics stable and predictable.
- Support consistent translation to HTTP responses at the boundary.
- Prevent low-level implementation details from leaking upward.

## Exception Layers

- Domain exceptions for invariant violations and business rule failures.
- Application exceptions for use-case level problems such as missing dependencies, conflicts, or forbidden operations.
- Infrastructure exceptions for database, network, or external system failures; translate them before they reach transport when possible.

## Rules

- Raise explicit exceptions for expected business failures.
- Do not use `ValueError` or generic `Exception` where a named error clarifies intent.
- Keep HTTP-specific exception types out of domain and service layers.
- Preserve enough structure on exceptions to support logging and response mapping.

## HTTP Mapping

- Map shared application and domain exceptions centrally in FastAPI exception handlers.
- Keep status-code semantics stable: validation, unauthorized, forbidden, not found, conflict, and unexpected failure should remain distinct.
- Do not leak raw SQLAlchemy or driver errors in public responses.
- Include safe machine-readable error codes where the project uses them.

## Design Guidance

- Prefer a small, coherent hierarchy over dozens of one-off exception classes.
- Reuse existing exceptions when the meaning matches exactly.
- If the caller needs structured context, put that context on the exception explicitly.
- Avoid control flow based on parsing exception message strings.

## Testing

- Test that services raise the intended exception type for known failure modes.
- Test FastAPI exception handlers map those exceptions to the right status and body.
- Test that unexpected infrastructure failures are logged and masked appropriately.

## Handoff

Return:
- exceptions added or changed
- layer where each exception is raised
- HTTP mapping notes
- logging or masking implications
- tests run
