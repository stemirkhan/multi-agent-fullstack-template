# Repository Conventions

This repository stores reusable multi-agent scaffolding for fullstack development.

Treat this repo as a template source of truth. Repository-level instructions should
govern how the reusable scaffolding is maintained, not how an installed target
project should behave.

## Canonical Layers

- Keep official Codex subagents in `.codex/agents/` as the canonical role layer.
- Keep official Codex skills in `.agents/skills/`.
- Keep workflows in `workflows/` as sequencing and handoff contracts, not role definitions.
- Treat `stack/default-stack.yaml` as the default architecture contract and stack SSOT.
- Treat `templates/project-AGENTS*.md` as the copy-ready target-project instruction layer.

## Authoring Rules

- Keep skills vendor-agnostic unless a Codex-specific behavior is unavoidable.
- Keep each `.agents/skills/*/SKILL.md` concise; move detailed procedures into `references/`, `scripts/`, or other bundled assets.
- Prefer reusable skills over adding new roles. Add a new subagent only when ownership boundaries are materially different.
- Keep repository `AGENTS.md` maintenance-focused. Put target-project operating guidance in `templates/project-AGENTS*.md`, not here.
- Avoid hard-coded local filesystem paths in skills or templates; all shipped assets should stay copy-safe.

## Stack Assumptions

- For backend defaults, prefer FastAPI controllers, service layer orchestration, Unit of Work transaction control, repositories, DTOs, explicit exceptions, structured logging, and Dishka DI.
- For frontend defaults, prefer TypeScript Vue with `Pinia`, composables, explicit feature and data-access boundaries, existing design-system reuse, and schema-driven validation.
- Keep framework-specific extensions explicitly optional. Do not let optional patterns leak back into the default Vue contract.

## Shipped Project Guardrails

- Keep repository `AGENTS.md` maintenance-focused, but ensure shipped project templates and shared backend skills enforce early port extraction, narrow family ports, no direct `application -> infrastructure` imports, and isolated test DB validation.
- When backend scaffolding changes, do not relax architectural guardrails in `templates/project-AGENTS*.md`, backend-oriented skills, or backend agent instructions.
- Keep structural-prep-first guidance consistent across repo-level workflows, backend skills, and project-level `AGENTS` templates so future projects receive the same stop conditions early.
- If a reusable backend change introduces a new dependency family, capability family, or orchestration seam, update the shared templates and skills in the same patch instead of leaving the template behind the latest lesson.

## Template Operating Procedure

- Before changing scaffold behavior, decide whether the change belongs in repo-maintenance guidance, shipped project templates, shared skills, workflows, or Codex agents.
- If a change affects both structure and behavior for installed projects, update the copy-ready project templates first or in the same patch; do not leave target-project instructions stale.
- If a change touches port extraction, service boundaries, provider isolation, or DI composition, update the relevant backend templates and skills in the same workstream.
- If implementation discovers boundary widening, a wrong landing zone, or a missing template sync, stop and update the template surface before continuing with more specialized drift.

## Synchronization Rules

When stack assumptions change:
- Update `stack/default-stack.yaml` first.
- Then sync `.agents/skills/project-conventions/conventions.md`.
- Then update affected skills, subagent `Read before acting` lists, prompts, templates, README, and QUICKSTART.
- Then run `bash scripts/check-integrity.sh`.

When a skill is added, removed, renamed, or re-scoped:
- Sync relevant `.codex/agents/*.toml` files.
- Sync README skill catalogs and install guidance.
- Sync QUICKSTART copy commands.
- Sync templates if agent routing, handoffs, or recommended usage changed.
- Run `bash scripts/check-integrity.sh`.

When workflows change:
- Keep YAML high-level and outcome-oriented.
- Put detailed operational procedures in skills, not in workflow files.
- Do not encode role definitions inside workflow steps.
- Sync any impacted project templates or agent handoff expectations in the same patch.
- Run `bash scripts/check-integrity.sh`.

## Repository-Specific Guidance

- Keep `project-conventions` aligned with the actual stack contract; it should refine `stack/default-stack.yaml`, not contradict it.
- Keep `code-review` as the default read-only review skill. Optional automation such as `codex-review-loop` should extend the template, not silently replace the default review path.
- If install surface changes, verify that partial-install commands remain copy-paste safe for backend-only and frontend-only setups.
