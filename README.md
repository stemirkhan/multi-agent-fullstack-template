# Multi-Agent Fullstack Template

Template repository for collecting:
- reusable skills for coding agents
- official Codex subagents
- canonical subagent role manifests
- shared workflows and prompt layers
- an explicit stack contract for backend and frontend work

## Quick Start

Install the template into a target project:

```sh
cp -R .codex .agents stack workflows /absolute/path/to/your-project/
```

Or install the skills globally for Codex:

```sh
mkdir -p "$HOME/.agents/skills"
cp -R .agents/skills/* "$HOME/.agents/skills/"
```

Then open the target project in Codex. For the full setup flow and notes about merging existing directories, see `QUICKSTART.md`.

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

### Frontend UI Work

```text
Spawn subagents for this frontend UI task.
Use frontend_ui_implementer for Vue component composition, Nuxt page or layout presentation, styling, responsiveness, and accessibility work.
Use reviewer_guard for the final review.
Wait for both subagents and summarize changed files, UI notes, tests, and residual risks.
Task: <describe the UI change here>
```

### Frontend Data And Validation Work

```text
Spawn subagents for this frontend client-logic task.
Use frontend_data_validation_implementer for typed API access, Nuxt async-data flows, Pinia state, and schema-driven validation changes.
Use integration_contract_keeper if request or response contracts might change.
Use reviewer_guard for the final review.
Wait for all results and summarize changed files, client-logic notes, tests, and residual risks.
Task: <describe the client behavior change here>
```

### Bugfix And Reproduction

```text
Spawn subagents for this bugfix.
Use qa_debugger to reproduce the issue and identify the failing path.
Use backend_implementer for backend fixes.
Use frontend_ui_implementer for presentation-heavy frontend fixes.
Use frontend_data_validation_implementer for client data, async-data, store, form, or validation fixes.
Use frontend_implementer only when the frontend fix is too small or too coupled to split.
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

### Browser Reproduction Or UI Verification

```text
Spawn subagents for this browser-heavy task.
Use tech_lead_orchestrator to decide whether the work belongs to QA, frontend, or both.
Use qa_debugger for agent-browser-based reproduction, screenshots, login handling, downloads, scraping, and verification.
Use frontend_ui_implementer for presentation-heavy app changes discovered during browser verification.
Use frontend_data_validation_implementer for client data, async-data, store, form, or validation fixes discovered during browser verification.
Use frontend_implementer only if the frontend change is too small or too coupled to split.
Wait for all results and summarize browser steps, artifacts, code changes, and residual risks.
Task: <describe the browser flow or website here>
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
Use tech_lead_orchestrator to break the task into backend, frontend UI, frontend data and validation, and contract work.
Use integration_contract_keeper for API and DTO contract alignment.
Use backend_implementer for backend changes.
Use frontend_ui_implementer for presentation-heavy frontend changes.
Use frontend_data_validation_implementer for async-data, store, form, and validation-heavy frontend changes.
Use frontend_implementer only when frontend work is too small or too coupled to split safely.
Use reviewer_guard for the final review.
Wait for all subagents and return one integrated summary with changed files, contract changes, tests run, and open risks.
Task: <describe the feature here>
```

## Target Stack

The repository is now biased toward this default architecture:

- Backend: `FastAPI`, `SQLAlchemy 2.x`, `Dishka`, `Alembic`
- Backend style: controller -> service -> unit of work -> repositories
- Backend boundaries: separate DTO layer, dedicated exceptions layer, structured logging
- Frontend: `Vue 3 + TypeScript`
- Frontend app framework: `Nuxt 3`
- Frontend shared state: `Pinia`
- Frontend data flow: typed API clients plus `useFetch` and `useAsyncData` through composables
- Frontend forms: composable-first forms with schema-driven validation

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

- Use TypeScript-first Vue patterns and avoid `any` by default.
- Keep Nuxt pages and layouts thin and move reusable behavior into composables and shared components.
- Keep typed API access in a dedicated data-access layer built around `useFetch`, `useAsyncData`, or project-standard wrappers.
- Use `Pinia` only for shared client state that truly crosses routes or features.
- Use schema-driven validation for forms and keep backend error mapping explicit.

## Skill Packs

Backend-oriented skills:
- `backend-structure`
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
- `frontend-structure`
- `frontend-feature`
- `vue`
- `nuxt`
- `pinia`
- `web-design-guidelines`
- `frontend-data-access`
- `frontend-forms-and-validation`

These frontend skills are taken from `antfu/skills` and then adapted locally to fit this repository's ownership boundaries and workflows.

Cross-cutting skills:
- `repo-intake`
- `task-decomposition`
- `code-review`
- `test-debug`
- `agent-browser`

## Frontend Specialization

- `frontend_ui_implementer` owns presentation-heavy work: Vue components, Nuxt page or layout presentation, styling, responsiveness, and accessibility.
- `frontend_data_validation_implementer` owns client behavior: typed API access, Nuxt async-data flows, Pinia state, and schema-driven validation.
- `frontend_implementer` remains the generalist fallback for small tasks or tightly coupled frontend work that is not worth splitting.
- When both specialists are active on one task, split file ownership explicitly instead of letting them edit the same frontend files in parallel.

## External Skill Donors

- `antfu/skills` is the upstream source for the frontend skill layer in this template, especially for `vue`, `nuxt`, `pinia`, and general web design guidance: https://github.com/antfu/skills
- Keep the local skills concise and adapted to this repository's ownership model instead of mirroring the upstream collection wholesale.

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
