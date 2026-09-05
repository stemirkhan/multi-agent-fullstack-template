# Backend Project Instructions

This file is meant to be copied into a backend-focused target project as
`AGENTS.md` and then completed with that project's exact commands and entrypoints.

## Purpose

- Define project-local operating instructions for Codex and Codex subagents.
- Point Codex at the installed `.codex/agents/`, `.agents/skills/`, and `stack/` layers.
- Keep backend implementation, debugging, migrations, release work, and review consistent.

## Default Agent Routing

- Use `tech_lead_orchestrator` first when the task spans multiple files, layers, or agents.
- Use `backend_implementer` for FastAPI, services, repositories, DTOs, exceptions, logging, and Unit of Work changes.
- Use `db_migration_owner` for schema changes, Alembic migrations, rollback planning, and data-shape compatibility.
- Use `devops_release_owner` for deployment, CI, observability, rollout, and rollback concerns.
- Use `qa_debugger` for reproduction, failing paths, regression checks, and risky validation seams.
- Use `reviewer_guard` for final review, release-blocking findings, and missing-test analysis.
- Before delegating, discover the agents actually installed under `.codex/agents/`; never route work to an unavailable role.

## Workflow Usage

- Prefer the installed backend profile workflows for feature delivery, bugfixes, and refactors.
- Treat workflows as sequencing and handoff contracts, not role definitions.
- Confirm every workflow role exists under `.codex/agents/` before execution.

## Stack Contract

Follow `stack/default-stack.yaml` unless the task explicitly changes the architecture.

Backend defaults:
- Keep I/O paths async from FastAPI through services, repositories, and Unit of Work; isolate blocking adapters.
- FastAPI controllers translate HTTP only.
- Services own use-case orchestration.
- Write transactions go through an explicit Unit of Work.
- Write repositories stay behind the Unit of Work; read-only use cases may use dedicated reader ports.
- Repository ports return domain entities or application-owned result types; infrastructure adapters map ORM rows before returning across those ports.
- Use Pydantic v2 for typed transport DTOs and settings; keep DTOs separate from ORM models and business invariants.
- Exceptions and logging stay explicit and structured.
- Application-layer modules must not import infrastructure implementations, ORM models, HTTP clients, or framework-specific adapters directly.
- Extract or confirm application ports before feature logic depends on provider-specific behavior, external systems, or persistence variants.
- Keep port families narrow by capability. Split reader, writer, provider, and policy concerns when responsibilities diverge.
- Keep final DTO assembly on reader/query seams when write flows need rich projection results.
- Treat emitted FastAPI OpenAPI, including route, status, header, authentication, and documented error declarations, as the public API definition.
- Persistence tests must use isolated test databases or transaction scopes, not dev or shared app databases.
- Keep authentication and authorization explicit, and keep secrets and sensitive payloads out of logs and public errors.

## Operating Procedure

- Before editing, choose the intended landing zone and decide whether structural prep is required first.
- If a task changes both structure and behavior, decompose it into at least two phases: structural prep first, then feature work.
- If a task touches port extraction, service boundaries, provider isolation, or DI composition, produce a short decomposition plan before implementation continues.
- If implementation discovers boundary widening, a wrong landing zone, or an unplanned external dependency family or cross-boundary capability seam, stop and route the work back through orchestration before continuing.
- Handoffs should record the chosen landing zone, whether structural prep was required or deferred, and any important boundary exceptions taken.

## Project-Specific Commands

- Record the real bootstrap, development, lint, type-check, test, migration, and release commands before relying on automation.
- Record the application entrypoint, generated artifacts, settings profiles, and the test-database fail-fast safeguard.
- Do not invent a missing command. Discover it from project manifests or ask the maintainer to document it.

## Browser Automation

- If the `agent-browser` CLI is available (`command -v agent-browser`), `qa_debugger` may use it for browser-driven repro against admin panels, docs, or verification surfaces.

## Expected Handoffs

When using multiple subagents, return:
- summary
- changed files
- tests run
- migration or rollout implications
- residual risks
- open questions and the owner of each follow-up
- clear ownership for any follow-up work
