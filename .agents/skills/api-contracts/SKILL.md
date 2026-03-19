---
name: api-contracts
description: Use when changing shared API contracts, Pydantic DTO schemas, OpenAPI surfaces, TypeScript clients, serialization rules, or frontend-backend integration boundaries.
---

# API Contracts

Use this skill when a change crosses the backend/frontend contract boundary and both sides need to stay aligned.

## Responsibilities

- Keep public request and response shapes explicit and stable.
- Coordinate backend DTO changes, OpenAPI changes, and frontend consumer impact.
- Surface compatibility risk early instead of after UI or backend implementation diverges.

## Default Workflow

1. Identify the contract surface that is changing: request, response, error body, pagination, filtering, auth context, or generated client type.
2. Decide whether the change is additive, behavior-changing, or breaking.
3. Update backend DTOs and transport definitions first.
4. Regenerate or update TypeScript client types if the project uses them.
5. Update frontend consumers and query or mutation hooks.
6. Verify serialization, error mapping, and backward compatibility.

## Rules

- Prefer additive contract changes over breaking changes.
- If a breaking change is unavoidable, document the migration path and impacted consumers.
- Keep pagination, sorting, filtering, and error shapes consistent across similar endpoints.
- Do not silently change enums, nullable behavior, or default semantics without checking consumers.
- Keep machine-readable fields stable when the frontend or integrations rely on them.

## Versioning And Compatibility

- Add new fields before removing old ones when staged rollout is possible.
- If old and new consumers must coexist, keep the response compatible long enough for rollout.
- Coordinate schema changes with frontend cache, forms, and validation assumptions.
- Treat error-body changes as contract changes, not incidental details.

## Verification

- Verify backend serialization matches the intended public shape.
- Verify generated or handwritten TypeScript clients match the backend contract.
- Verify frontend consumers still parse and render the changed data correctly.
- Add or update contract-sensitive tests where the risk is material.

## Handoff

Return:
- contract surfaces changed
- compatibility level: additive, behavior-changing, or breaking
- consumers impacted
- regeneration or sync steps required
- tests run
