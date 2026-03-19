---
name: backend-dtos
description: Use when designing backend DTOs for request, response, command, query, or inter-layer contracts separate from ORM entities and framework objects.
---

# Backend DTOs

Use this skill when data crosses a layer boundary and should not leak ORM models or raw framework objects.

## Responsibilities

- Define explicit shapes for input and output between transport, service, and integration boundaries.
- Keep contracts stable and typed.
- Separate public API shapes from internal persistence models.
- Make validation and serialization intent obvious.

## DTO Taxonomy

- Request DTOs: transport-layer input models.
- Response DTOs: transport-layer output models.
- Command DTOs: inputs to write use cases.
- Query DTOs: inputs to read use cases.
- Result DTOs: typed service outputs.

## Rules

- Do not use ORM models as DTOs.
- Do not overload one DTO for unrelated layers just to reduce file count.
- Prefer explicit optionality and defaults.
- Name DTOs by role, not by vague suffixes alone.
- Keep backward compatibility in mind for public API DTOs.

## Mapping Guidance

- Controllers map request models to service inputs when the shapes differ.
- Services return result DTOs or domain results that controllers can map to response DTOs.
- Repository-layer data structures should not leak directly into response contracts.
- Keep mapping logic close to the boundary where the shape changes.

## Validation And Serialization

- Validate as early as the boundary that owns the rule.
- Keep transport validation in request models and business validation in services.
- Use serialization rules deliberately for enums, datetimes, decimals, and IDs.
- Avoid silent lossy conversions.

## Compatibility

- When changing public responses, identify affected consumers explicitly.
- Prefer additive changes before breaking changes.
- If a breaking change is unavoidable, surface it through the contract workflow and migration notes.

## Testing

- Test parsing and serialization of tricky fields.
- Test mapping when shapes differ across layers.
- Test optional and defaulted fields explicitly.
- Add contract tests for critical public DTOs when consumers depend on exact shapes.

## Handoff

Return:
- DTOs added or changed
- boundary where each DTO is used
- mapping points introduced or updated
- compatibility notes
- tests run
