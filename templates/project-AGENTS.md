# Project Instructions

This file is meant to be copied into a target project as `AGENTS.md` and then
completed with that project's exact commands and entrypoints.

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
- Use `devops_release_owner` for CI, deployment, runtime configuration, observability, rollout, and rollback work.
- Use `qa_debugger` for reproduction, failing paths, regression checks, and browser-heavy verification.
- Use `reviewer_guard` for final review, release-blocking findings, and missing-test analysis.
- Before delegating, discover the agents actually installed under `.codex/agents/`; never route work to an unavailable role.

## Workflow Usage

- Prefer `workflows/feature-delivery.yaml` for cross-layer features.
- Prefer `workflows/bugfix.yaml` for reproduction-first fixes.
- Prefer `workflows/refactor.yaml` for behavior-preserving structural changes.
- Treat workflows as sequencing and handoff contracts, not as role definitions.

## Stack Contract

Follow `stack/default-stack.yaml` unless the task explicitly changes the architecture.

Backend defaults:
- Keep I/O paths async from FastAPI through services, repositories, and Unit of Work; isolate blocking adapters.
- FastAPI controllers translate HTTP only.
- Services own use-case orchestration.
- Write transactions go through an explicit Unit of Work.
- Write repositories stay behind the Unit of Work; read-only use cases may use dedicated reader ports.
- Use Pydantic v2 for typed transport DTOs and settings; keep DTOs separate from ORM models and business invariants.
- Exceptions and logging stay explicit and structured.

Frontend defaults:
- TypeScript-first Vue 3.
- Keep route views and screen-level entry components thin.
- Put reusable behavior in composables.
- Use Pinia only for shared client state that truly crosses features or views.
- Keep typed API access in dedicated data-access seams.
- Keep server state, request status, refresh, and invalidation in data-access/query seams; use Pinia only for shared client-owned state.
- Keep transient presentation and form state local unless a real cross-feature owner exists.
- Keep forms schema-driven and backend error mapping explicit.

Backend guardrails for backend portions of the project:
- Application-layer modules must not import infrastructure implementations, ORM models, raw HTTP clients, or framework-specific adapters directly.
- Extract or confirm application ports before feature logic depends on provider-specific behavior, external systems, or persistence variants.
- Keep port families narrow by capability. Split reader, writer, provider, and policy concerns when responsibilities diverge.
- When a write use case returns a rich DTO, keep final DTO assembly on a reader port or dedicated query seam instead of widening the mutation port.
- Treat emitted FastAPI OpenAPI, including route, status, header, authentication, and documented error declarations, as the public API definition.
- Tests that cover persistence behavior must use isolated test databases or transaction scopes, not dev or shared app databases.
- Keep authentication and authorization enforced on the backend, and keep secrets and sensitive payloads out of logs and client code.

## Operating Procedure

- Before editing, choose the intended landing zone and decide whether structural prep is required first.
- If a task changes both structure and behavior, decompose it into at least two phases: structural prep first, then feature work.
- If a task touches port extraction, service boundaries, provider isolation, frontend data-access seams, or DI composition, produce a short decomposition plan before implementation continues.
- If implementation discovers boundary widening, a wrong landing zone, or an unplanned external dependency family or cross-boundary capability seam, stop and route the work back through orchestration before continuing.
- Handoffs should record the chosen landing zone, whether structural prep was required or deferred, and any important boundary exceptions taken.

## Project-Specific Commands

- Record the real bootstrap, development, lint, type-check, test, migration, build, and release commands for this project here before relying on automation.
- Record the backend and frontend entrypoints, generated artifacts, and any commands that must not run against shared environments.
- Do not invent a missing command. Discover it from project manifests or ask the maintainer to document it.

## Browser Automation

- If the `agent-browser` CLI is available (`command -v agent-browser`), use it for browser-heavy reproduction, screenshots, scraping, downloads, and login-driven UI verification.
- Keep browser automation in `qa_debugger` by default, or in frontend agents for targeted UI verification.

## Expected Handoffs

When using multiple subagents, return:
- summary
- changed files
- tests run
- contract or migration implications
- environment, rollout, or rollback implications
- residual risks
- open questions and the owner of each follow-up
- clear ownership for any follow-up work
