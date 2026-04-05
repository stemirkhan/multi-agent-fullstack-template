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

## Browser Automation

- If `agent-browser` is installed, `qa_debugger` may still use it for browser-driven repro against admin panels, docs, or verification surfaces.

## Expected Handoffs

When using multiple subagents, return:
- changed files
- tests run
- migration or rollout implications
- residual risks
- clear ownership for any follow-up work
