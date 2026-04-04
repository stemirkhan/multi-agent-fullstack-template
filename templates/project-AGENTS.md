# Project Instructions

This file is meant to be copied into a target project as `AGENTS.md`.

## Purpose

- Define project-local operating instructions for Codex and Codex subagents.
- Point Codex at the installed `.codex/agents/`, `.agents/skills/`, `stack/`, and `workflows/` layers.
- Keep multi-agent execution consistent across feature work, bugfixes, refactors, and reviews.

## Default Agent Routing

- Use `tech_lead_orchestrator` first when the task spans multiple files, layers, or agents.
- Use `backend_implementer` for FastAPI, services, repositories, DTOs, exceptions, logging, and Unit of Work changes.
- Use `frontend_ui_implementer` for Vue and Nuxt presentation work: components, layouts, styling, accessibility, and responsive behavior.
- Use `frontend_data_validation_implementer` for typed API access, Nuxt async-data flows, Pinia state, forms, and schema-driven validation.
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
- TypeScript-first Vue with Nuxt 3.
- Keep pages and layouts thin.
- Put reusable behavior in composables.
- Use Pinia only for shared client state that truly crosses routes or features.
- Keep typed API access in dedicated data-access seams.
- Keep forms schema-driven and backend error mapping explicit.

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
