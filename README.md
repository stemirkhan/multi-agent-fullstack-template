# Multi-Agent Fullstack Template

Template repository for collecting:
- reusable skills for coding agents
- official Codex subagents
- canonical subagent role manifests
- shared workflows and prompt layers
- an explicit stack contract for backend and frontend work

## Quick Subagent Prompts

Paste one of these prompts into Codex from a project that already contains this template.

### Backend Feature

```text
Spawn subagents for this backend task.
Use tech_lead_orchestrator to decompose the work first.
Then use backend_implementer for implementation and reviewer_guard for the final review.
Wait for all subagents and return one consolidated summary with changed files, tests run, and open risks.
Task: <describe the backend feature here>
```

### Bugfix And Reproduction

```text
Spawn subagents for this bugfix.
Use qa_debugger to reproduce the issue and identify the failing path.
Use backend_implementer or frontend_implementer for the fix, depending on the layer involved.
Use reviewer_guard for a final regression review.
Wait for all results and summarize root cause, fix, tests, and residual risks.
Bug: <describe the bug here>
```

### Code Review

```text
Spawn subagents for a review of the current branch against main.
Use reviewer_guard for the main review.
Use qa_debugger to inspect test gaps and flaky behavior.
Wait for both subagents and summarize findings by severity, then list missing tests and rollout risks.
```

### Database Migration

```text
Spawn subagents for this schema change.
Use db_migration_owner for the migration plan and migration changes.
Use backend_implementer to update repositories, DTOs, services, and controllers affected by the schema change.
Use reviewer_guard for a final migration and rollback review.
Wait for all subagents and summarize migration steps, compatibility risks, rollback plan, and tests.
Task: <describe the schema or data change here>
```

### Fullstack Feature

```text
Spawn subagents for this fullstack feature.
Use tech_lead_orchestrator to break the task into backend, frontend, and contract work.
Use integration_contract_keeper for API and DTO contract alignment.
Use backend_implementer for backend changes.
Use frontend_implementer for frontend changes.
Use reviewer_guard for the final review.
Wait for all subagents and return one integrated summary with changed files, contract changes, tests run, and open risks.
Task: <describe the feature here>
```

## Target Stack

The repository is now biased toward this default architecture:

- Backend: `FastAPI`, `SQLAlchemy 2.x`, `Dishka`, `Alembic`
- Backend style: controller -> service -> unit of work -> repositories
- Backend boundaries: separate DTO layer, dedicated exceptions layer, structured logging
- Frontend: `React + TypeScript`
- UI system: `shadcn/ui` on top of `Radix UI` and `Tailwind CSS`
- Frontend data flow: `TanStack Query`
- Frontend forms: `React Hook Form + Zod`

The canonical stack contract lives in `stack/default-stack.yaml`.

## Layout

```text
.codex/             # official Codex config and subagents
.agents/skills/     # official Codex skills
stack/              # explicit tech and architecture assumptions
agents/roles/       # canonical internal role manifests
prompts/common/     # internal role prompts and stack constraints
workflows/          # default multi-agent execution flows
```

## Backend Architecture Rules

- FastAPI controllers should translate HTTP input and output only and call services.
- Services own application use cases and transaction boundaries.
- Transaction management should go through a Unit of Work abstraction.
- Repositories should sit behind the Unit of Work and hide direct session usage.
- DTOs should be separate from ORM models and HTTP framework objects.
- Domain and application exceptions should be mapped to HTTP responses at the boundary.
- Logging should be structured and consistent across request and use-case boundaries.

## Frontend Architecture Rules

- Use TypeScript-first React patterns and avoid `any` by default.
- Prefer ready-made accessible components from `shadcn/ui` before custom primitives.
- Keep server-state logic in a dedicated data-access layer with `TanStack Query`.
- Use `React Hook Form` and `Zod` for forms and validation-heavy flows.
- Keep route and container code thin and move reusable UI into shared components.

## Skill Packs

Backend-oriented skills:
- `backend-feature`
- `fastapi-controllers`
- `dishka-di`
- `service-layer`
- `sqlalchemy-repositories`
- `unit-of-work`
- `backend-dtos`
- `backend-exceptions`
- `backend-logging`
- `db-migration`
- `api-contracts`

Frontend-oriented skills:
- `frontend-feature`
- `frontend-typescript-react`
- `frontend-shadcn-ui`
- `frontend-data-access`
- `frontend-forms-and-validation`

## Design Rules

- `.codex/agents/` and `.agents/skills/` are the copy-ready official Codex layer.
- `agents/roles/` remains the internal source of truth for role intent.
- Skills should stay small and composable.
- Workflows should describe sequencing between roles, not tool implementation details.
- Stack-specific constraints belong in prompts and stack manifests, not duplicated in every role.

## Reuse Modes

- `Project-scoped Codex`: copy `.codex/`, `.agents/`, `stack/`, and `workflows/` into a target repository
- `User-scoped Codex`: optionally copy `.agents/skills/*` into `$HOME/.agents/skills/`

See `QUICKSTART.md` for the exact commands.

## Current Status

This repository now contains:
- completed stack-aware skills
- official Codex subagents in `.codex/agents/*.toml`
- official Codex skill directories in `.agents/skills/*`
- canonical role manifests
- baseline prompts, workflows, and stack manifest

The YAML files in `agents/roles/` remain internal source manifests that describe role intent. The copy-ready Codex layer is the `.codex/` plus `.agents/skills/` structure.
