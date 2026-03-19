---
name: backend-logging
description: Use when implementing structured logging, correlation IDs, request tracing, service-level diagnostics, or failure logging in the Python backend.
---

# Backend Logging

Use this skill when logs need to help operators and developers understand requests, use cases, failures, and integrations without flooding output.

## Responsibilities

- Keep logs structured, searchable, and consistent across layers.
- Correlate request-level and service-level events.
- Capture enough context for diagnosis without leaking secrets.
- Log business-significant transitions and failures, not every line of code.

## Default Conventions

- Prefer structured key-value logging over free-form prose.
- Include stable identifiers when available: request ID, user ID, account ID, aggregate ID, job ID.
- Keep event names explicit and predictable.
- Reuse the project logging setup rather than instantiating ad hoc loggers everywhere.

## Where To Log

- At request entry and completion for boundary visibility.
- At service boundaries for important business actions.
- Around external integrations and retries.
- On exception handling paths, especially before masking or translation.

## Where Not To Log

- Inside tight loops unless diagnosing a specific hot path.
- Raw secrets, tokens, passwords, session cookies, or full personal payloads.
- Repetitive noise that duplicates framework access logs without adding value.

## Correlation

- Propagate request or trace IDs through FastAPI middleware, service calls, and async jobs where possible.
- If background jobs continue work started by a request, carry a correlation ID forward explicitly.
- Make sure structured context survives exception handling paths.

## Failure Logging

- Log enough context to identify the failing use case and boundary.
- Keep public error responses sanitized even if internal logs are detailed.
- Avoid double-logging the same failure at every layer; log once per meaningful boundary.

## Testing And Verification

- Verify critical paths emit the expected structured fields.
- Verify sensitive values are redacted or omitted.
- Verify request correlation appears in both happy-path and failure-path logs.
- For important incident-prone flows, keep at least one integration check or snapshot of expected log shape.

## Handoff

Return:
- logging points added or changed
- structured fields introduced
- correlation or context propagation notes
- redaction decisions
- tests or manual verification run
