# Backend Project Instructions

This file is meant to be copied into a backend-focused target project as `AGENTS.md`.

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

## Stack Contract

Follow `stack/default-stack.yaml` unless the task explicitly changes the architecture.

Backend defaults:
- FastAPI controllers translate HTTP only.
- Services own use-case orchestration.
- Transactions go through an explicit Unit of Work.
- Repositories stay behind the Unit of Work.
- DTOs stay separate from ORM models.
- Exceptions and logging stay explicit and structured.
- Application-layer modules must not import infrastructure implementations, ORM models, HTTP clients, or framework-specific adapters directly.
- Extract or confirm application ports before feature logic depends on provider-specific behavior, external systems, or persistence variants.
- Keep port families narrow by capability. Split reader, writer, provider, and policy concerns when responsibilities diverge.
- Keep final DTO assembly on reader/query seams when write flows need rich projection results.
- Persistence tests must use isolated test databases or transaction scopes, not dev or shared app databases.

## Operating Procedure

- Before editing, choose the intended landing zone and decide whether structural prep is required first.
- If a task changes both structure and behavior, decompose it into at least two phases: structural prep first, then feature work.
- If a task touches port extraction, service boundaries, provider isolation, or DI composition, produce a short decomposition plan before implementation continues.
- If implementation discovers boundary widening, a wrong landing zone, or an unexpected new dependency family, stop and route the work back through orchestration before continuing.
- Handoffs should record the chosen landing zone, whether structural prep was required or deferred, and any important boundary exceptions taken.

## Browser Automation

- If `agent-browser` is installed, `qa_debugger` may still use it for browser-driven repro against admin panels, docs, or verification surfaces.

## Expected Handoffs

When using multiple subagents, return:
- changed files
- tests run
- migration or rollout implications
- residual risks
- clear ownership for any follow-up work
