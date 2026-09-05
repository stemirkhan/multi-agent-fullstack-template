# Multi-Agent Fullstack Template

![Codex](https://img.shields.io/badge/Codex-subagents%20%2B%20skills-412991)
![Backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20SQLAlchemy-0f766e)
![Frontend](https://img.shields.io/badge/frontend-Vue%20%2B%20Pinia-1d4ed8)
![Install](https://img.shields.io/badge/install-full%20or%20partial-f59e0b)
![Browser](https://img.shields.io/badge/browser-agent--browser%20optional-64748b)

> Copy-ready Codex subagents, skills, workflows, and project `AGENTS.md` templates for a FastAPI + Vue fullstack stack.

This repository packages a reusable multi-agent setup for projects that want:
- project-scoped Codex agents in `.codex/agents/`
- project-scoped Codex skills in `.agents/skills/`
- a clear architectural contract in `stack/default-stack.yaml`
- repeatable multi-agent sequencing through `workflows/`
- project-level `AGENTS.md` templates for fullstack, backend-only, and frontend-only installs

## TL;DR

Use the safe installer from this repository:

```bash
python3 scripts/install.py --profile full --target /absolute/path/to/your-project --dry-run
python3 scripts/install.py --profile full --target /absolute/path/to/your-project
```

Replace `full` with `backend` or `frontend` for a partial install. The installer
preflights conflicts, refuses silent overwrite, and rolls back handled write
failures before commit. It verifies installed file and parent identities from
the target root before commit and blocks completion if it detects a concurrent
move or replacement. Interrupting cleanup after commit keeps the installed
files and reports that state explicitly. Applying a profile currently requires
Linux or macOS; see the [Quickstart](QUICKSTART.md) for the filesystem and
crash-consistency limits.

- Fullstack project: install the `full` profile
- Backend-only project: install the `backend` profile
- Frontend-only project: install the `frontend` profile
- Browser automation: install `agent-browser` separately if you want browser-driven verification

## What You Get

| Layer | Purpose |
| --- | --- |
| `.codex/agents/` | Canonical Codex subagents for orchestration, implementation, debugging, migrations, contracts, release work, and review |
| `.agents/skills/` | Reusable skill packs for backend, frontend, debugging, decomposition, and browser automation |
| `templates/` | Copy-ready `AGENTS.md` files for target projects |
| `workflows/` | Default multi-agent execution flows for features, bugfixes, and refactors |
| `stack/default-stack.yaml` | Explicit backend and frontend architecture contract |
| `distribution/profiles.toml` | Canonical contents of fullstack and partial install profiles |
| `scripts/` and `tests/` | Safe installer, integrity validation, and regression tests |

## Install Modes

| Mode | Best for | What to install |
| --- | --- | --- |
| Full project install | Fullstack repos that want the whole setup | `.codex/`, `.agents/`, `stack/`, `workflows/`, and `AGENTS.md` |
| Backend-only install | API or service repos | Backend-focused agents, skills, profile workflows, `stack/`, and backend `AGENTS.md` |
| Frontend-only install | UI repos | Frontend-focused agents, skills, profile workflows, `stack/`, and frontend `AGENTS.md` |

Primary full install:

```bash
python3 scripts/install.py --profile full --target /absolute/path/to/your-project --dry-run
python3 scripts/install.py --profile full --target /absolute/path/to/your-project
```

For partial-install guidance, see [QUICKSTART.md](QUICKSTART.md).

## How It Fits Together

```mermaid
flowchart LR
    A[AGENTS.md] --> B[.codex/agents]
    B --> C[.agents/skills]
    B --> D[workflows]
    B --> E[stack/default-stack.yaml]
    D --> F[task sequencing and handoffs]
    C --> G[execution guidance]
    E --> H[architecture constraints]
```

## Repository Layout

```text
AGENTS.md                    # repository maintenance instructions for this template repo
.codex/
  config.toml
  agents/                    # canonical Codex subagents
.agents/
  skills/                    # project-scoped Codex skills
distribution/
  profiles.toml              # install profile source of truth
scripts/
  install.py                 # conflict-safe installer
  check-integrity.sh         # canonical validation entrypoint
stack/
  default-stack.yaml         # architecture contract
templates/
  project-AGENTS.md
  project-AGENTS.backend.md
  project-AGENTS.frontend.md
workflows/                   # sequencing and handoff contracts
tests/                       # installer and integrity regression tests
```

## Agent Catalog

| Agent | Owns | Use when |
| --- | --- | --- |
| `tech_lead_orchestrator` | task decomposition, ownership, sequencing | the task spans multiple files, layers, or specialists |
| `backend_implementer` | FastAPI, services, repositories, DTOs, exceptions, logging, UoW | backend behavior changes |
| `frontend_ui_implementer` | Vue presentation, route-view composition, styling, accessibility | the work is primarily visual or interaction-heavy |
| `frontend_data_validation_implementer` | typed API access, async-data, Pinia, forms, validation | the work is primarily client logic or data flow |
| `frontend_implementer` | tightly coupled mixed frontend work | the task is too small or coupled to split safely |
| `integration_contract_keeper` | routes, statuses, headers, auth, DTO/OpenAPI, errors, and consumer alignment | any public API declaration changes |
| `db_migration_owner` | schema change planning, Alembic, rollback | persistence shape changes |
| `devops_release_owner` | CI, deployment, rollout, rollback, observability | release or infra concerns are involved |
| `qa_debugger` | reproduction, failing paths, regression checks, browser verification | you need to debug or verify behavior |
| `reviewer_guard` | final review, risk analysis, missing tests | you want a final read-only review |

## How To Choose An Agent

| If the task is mostly about... | Start with... |
| --- | --- |
| multi-step planning across layers | `tech_lead_orchestrator` |
| FastAPI/backend implementation | `backend_implementer` |
| Vue UI, route-view composition, styling, accessibility | `frontend_ui_implementer` |
| frontend data flow, forms, Pinia, validation | `frontend_data_validation_implementer` |
| mixed but small frontend changes | `frontend_implementer` |
| API route, status, header, auth, DTO, error, or consumer drift | `integration_contract_keeper` |
| schema changes or Alembic | `db_migration_owner` |
| CI, deployment, rollout, or observability | `devops_release_owner` |
| reproduction, failing paths, browser checks | `qa_debugger` |
| final review and regression risk | `reviewer_guard` |

## Workflow Catalog

| Workflow | Goal | Typical use |
| --- | --- | --- |
| `feature-delivery` | deliver a feature with explicit ownership and review | cross-layer feature work |
| `bugfix` | reproduce first, then isolate and verify the fix | correctness or regression issues |
| `refactor` | reshape code without changing intended behavior | structural cleanup with invariant preservation |

Workflows are sequencing and handoff contracts, not role definitions.

## Prompt Starters

Use these from a target project that already contains the installed template.

<details>
<summary>Backend Feature</summary>

```text
Spawn subagents for this backend task.
Use tech_lead_orchestrator to decompose the work first.
Then use backend_implementer for implementation and reviewer_guard for the final review.
Wait for all subagents and return one consolidated summary with changed files, tests run, and open risks.
Task: <describe the backend feature here>
```

</details>

<details>
<summary>Frontend UI Work</summary>

```text
Spawn subagents for this frontend UI task.
Use frontend_ui_implementer for Vue component composition, route-view or app-shell presentation, styling, responsiveness, and accessibility work.
Use reviewer_guard for the final review.
Wait for both subagents and summarize changed files, UI notes, tests, and residual risks.
Task: <describe the UI change here>
```

</details>

<details>
<summary>Frontend Data And Validation Work</summary>

```text
Spawn subagents for this frontend client-logic task.
Use frontend_data_validation_implementer for typed API access, composable-driven data flows, Pinia state, and schema-driven validation changes.
Use integration_contract_keeper if any public API declaration might change.
Use reviewer_guard for the final review.
Wait for all results and summarize changed files, client-logic notes, tests, and residual risks.
Task: <describe the client behavior change here>
```

</details>

<details>
<summary>Bugfix And Reproduction</summary>

```text
Spawn subagents for this bugfix.
Use qa_debugger to reproduce the issue and identify the failing path.
Use backend_implementer for backend fixes.
Use frontend_ui_implementer for presentation-heavy frontend fixes.
Use frontend_data_validation_implementer for client data, async-data, store, form, or validation fixes.
Use frontend_implementer only when the frontend fix is too small or too coupled to split.
Use qa_debugger again after implementation to reproduce the original failure and check adjacent regressions.
Use reviewer_guard for a final regression review.
Wait for all results and summarize root cause, fix, tests, and residual risks.
Bug: <describe the bug here>
```

</details>

<details>
<summary>Browser Reproduction Or UI Verification</summary>

```text
Spawn subagents for this browser-heavy task.
Use tech_lead_orchestrator to decide whether the work belongs to QA, frontend, or both.
If the agent-browser CLI is available, use qa_debugger for browser-based reproduction, screenshots, login handling, downloads, scraping, and verification.
Use frontend_ui_implementer for presentation-heavy app changes discovered during browser verification.
Use frontend_data_validation_implementer for client data, async-data, store, form, or validation fixes discovered during browser verification.
Use frontend_implementer only if the frontend change is too small or too coupled to split.
Wait for all results and summarize browser steps, artifacts, code changes, and residual risks.
Task: <describe the browser flow or website here>
```

</details>

<details>
<summary>Database Migration</summary>

```text
Spawn subagents for this schema change.
Use db_migration_owner for the migration plan and migration changes.
Use backend_implementer to update repositories, DTOs, services, and controllers affected by the schema change.
Use reviewer_guard for a final migration and rollback review.
Wait for all subagents and summarize migration steps, compatibility risks, rollback plan, and tests.
Task: <describe the schema or data change here>
```

</details>

<details>
<summary>Fullstack Feature</summary>

```text
Spawn subagents for this fullstack feature.
Use tech_lead_orchestrator to break the task into backend, frontend UI, frontend data and validation, and contract work.
Use integration_contract_keeper for route, status, header, auth, DTO, error, and consumer alignment.
Use backend_implementer for backend changes.
Use frontend_ui_implementer for presentation-heavy frontend changes.
Use frontend_data_validation_implementer for async-data, store, form, and validation-heavy frontend changes.
Use frontend_implementer only when frontend work is too small or too coupled to split safely.
Use reviewer_guard for the final review.
Wait for all subagents and return one integrated summary with changed files, contract changes, tests run, and open risks.
Task: <describe the feature here>
```

</details>

<details>
<summary>Code Review</summary>

```text
Spawn subagents for a review of the current branch against main.
Use reviewer_guard for the main review.
Use qa_debugger to inspect test gaps and flaky behavior.
Wait for both subagents and summarize findings by severity, then list missing tests and rollout risks.
```

</details>

## Default Stack

### Backend

| Concern | Default |
| --- | --- |
| Framework | `FastAPI` |
| Validation/settings | `Pydantic v2` with explicit settings boundaries |
| ORM | `SQLAlchemy 2.x` |
| DI | `Dishka` |
| Migrations | `Alembic` |
| Architecture | controller -> service -> unit of work -> repositories |
| Boundaries | dedicated DTO layer, explicit exceptions, structured logging |
| Contracts | OpenAPI-aligned backend DTOs and typed frontend consumers |

Backend rules:
- keep I/O paths async and isolate blocking adapters
- controllers translate HTTP only and call services
- services own use-case orchestration and transaction boundaries
- write repositories stay behind the unit of work; read-only use cases may use dedicated reader ports
- DTOs stay separate from ORM and transport types
- exceptions and logging stay explicit and structured

### Frontend

| Concern | Default |
| --- | --- |
| Framework | `Vue 3 + TypeScript` |
| Shared state | `Pinia` |
| Data flow | typed API clients, explicit server-state boundaries, and composable-driven flows |
| Forms | composable-first with schema-driven validation |

Frontend rules:
- keep route views and screen-level entry components thin
- move reusable behavior into composables and shared components
- keep typed API access in dedicated data-access seams
- keep server state and invalidation in data-access/query seams
- use `Pinia` only for shared client-owned state that truly crosses features or views
- keep forms schema-driven and backend error mapping explicit

The canonical stack contract lives in [`stack/default-stack.yaml`](stack/default-stack.yaml).

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
- `devops-release`

Frontend-oriented skills:
- `frontend-structure`
- `frontend-feature`
- `vue`
- `pinia`
- `web-design-guidelines`
- `frontend-data-access`
- `frontend-forms-and-validation`

Cross-cutting skills:
- `project-conventions`
- `repo-intake`
- `task-decomposition`
- `code-review`
- `test-debug`
- `agent-browser`

Advanced optional skills:
- `codex-review-loop` for deeper PR, branch, or uncommitted-change audits through Codex CLI

Frontend skill source:
- the frontend skills are taken from [`antfu/skills`](https://github.com/antfu/skills)
- they are then adapted locally to fit this repository's ownership boundaries and workflows

## Project Templates

Copy-ready project instruction files:
- `templates/project-AGENTS.md` for fullstack installs
- `templates/project-AGENTS.backend.md` for backend-only installs
- `templates/project-AGENTS.frontend.md` for frontend-only installs

## Design Principles

- `.codex/agents/` and `.agents/skills/` are the canonical Codex layer in this template
- skills should stay small and composable
- workflows describe sequencing and handoffs, not tool implementation details
- stack-specific constraints originate in the stack manifest and stay synchronized with templates and skills
- agents load task-relevant skills progressively instead of reading the entire catalog up front
- reusable agents inherit the parent model unless a target project deliberately opts into a model-specific profile
- frontend specialist agents should not edit the same files in parallel without explicit ownership

## Reuse Modes

- `Project-scoped Codex`: use `scripts/install.py --profile full`
- `Partial install`: use the `backend` or `frontend` installer profile when the target project does not need the full role set
- `User-scoped Codex`: install only individually reviewed, self-contained skills; bulk-copying this project-scoped catalog is unsupported

## Validate This Template

```bash
python3 -m pip install --requirement requirements-validation.txt
bash scripts/check-integrity.sh
python3 -m unittest discover -s tests -v
```

The installer itself uses only the Python standard library. The integrity check
uses the pinned PyYAML validation dependency to parse the stack and workflows,
and validates canonical agents, skills, documentation catalogs, review output
schema, and all install profiles. CI runs the same commands so a partial-install
dependency cannot silently drift. Source tooling is tested on Python 3.12
through 3.14.

## Current Contents

This repository currently contains:
- project-scoped Codex agents in `.codex/agents/*.toml`
- project-scoped Codex skill directories in `.agents/skills/*`
- copy-ready project `AGENTS.md` templates
- shared workflows and profile-aware installation metadata
- a stack-aware architecture contract
