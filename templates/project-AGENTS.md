# Project Instructions

This file is meant to be copied into a target project as `AGENTS.md`.

## Purpose

- Define project-local operating instructions for Codex and Codex subagents.
- Point Codex at the installed `.codex/agents/`, `.agents/skills/`, `stack/`, and `workflows/` layers.
- Keep multi-agent execution consistent across feature work, bugfixes, refactors, and reviews.

## Default Agent Routing

- Use `tech_lead_orchestrator` first when the task spans multiple files, layers, or agents.
- Use `backend_implementer` for FastAPI, services, repositories, DTOs, exceptions, logging, and Unit of Work changes.
- Use `frontend_ui_implementer` for Vue presentation work: components, route views, app shell, styling, accessibility, and responsive behavior.
- Use `frontend_data_validation_implementer` for typed API access, composable-driven data flows, Pinia state, forms, and schema-driven validation.
- Use `frontend_implementer` only for small frontend tasks that are too coupled to split safely.
- Use `integration_contract_keeper` when request, response, OpenAPI, or frontend-consumer contracts change.
- Use `db_migration_owner` for schema changes, Alembic migrations, and rollback planning.
- Use `qa_debugger` for reproduction, failing paths, regression checks, and browser-heavy verification.
- Use `reviewer_guard` for final review, release-blocking findings, and missing-test analysis.

## Workflow Usage

- Prefer `workflows/feature-delivery.yaml` for cross-layer features.
- Prefer `workflows/bugfix.yaml` for reproduction-first fixes.
- Prefer `workflows/refactor.yaml` for behavior-preserving structural changes.
- Treat workflows as sequencing and handoff contracts, not as role definitions.

## Stack Contract

Follow `stack/default-stack.yaml` unless the task explicitly changes the architecture.

Backend defaults:
- FastAPI controllers translate HTTP only.
- Services own use-case orchestration.
- Transactions go through an explicit Unit of Work.
- Repositories stay behind the Unit of Work.
- DTOs stay separate from ORM models.
- Exceptions and logging stay explicit and structured.

Frontend defaults:
- TypeScript-first Vue 3.
- Keep route views and screen-level entry components thin.
- Put reusable behavior in composables.
- Use Pinia only for shared client state that truly crosses features or views.
- Keep typed API access in dedicated data-access seams.
- Keep forms schema-driven and backend error mapping explicit.

Backend guardrails for backend portions of the project:
- Application-layer modules must not import infrastructure implementations, ORM models, raw HTTP clients, or framework-specific adapters directly.
- Extract or confirm application ports before feature logic depends on provider-specific behavior, external systems, or persistence variants.
- Keep port families narrow by capability. Split reader, writer, provider, and policy concerns when responsibilities diverge.
- When a write use case returns a rich DTO, keep final DTO assembly on a reader port or dedicated query seam instead of widening the mutation port.
- Tests that cover persistence behavior must use isolated test databases or transaction scopes, not dev or shared app databases.

## Operating Procedure

- Before editing, choose the intended landing zone and decide whether structural prep is required first.
- If a task changes both structure and behavior, decompose it into at least two phases: structural prep first, then feature work.
- If a task touches port extraction, service boundaries, provider isolation, frontend data-access seams, or DI composition, produce a short decomposition plan before implementation continues.
- If implementation discovers boundary widening, a wrong landing zone, or an unexpected new dependency family, stop and route the work back through orchestration before continuing.
- Handoffs should record the chosen landing zone, whether structural prep was required or deferred, and any important boundary exceptions taken.

## Browser Automation

- If `agent-browser` is installed, use it for browser-heavy reproduction, screenshots, scraping, downloads, and login-driven UI verification.
- Keep browser automation in `qa_debugger` by default, or in frontend agents for targeted UI verification.

## Expected Handoffs

When using multiple subagents, return:
- changed files
- tests run
- contract or migration implications
- residual risks
- clear ownership for any follow-up work
