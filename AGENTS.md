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

## Synchronization Rules

When stack assumptions change:
- Update `stack/default-stack.yaml` first.
- Then sync `.agents/skills/project-conventions/conventions.md`.
- Then update affected skills, subagent `Read before acting` lists, prompts, templates, README, and QUICKSTART.

When a skill is added, removed, renamed, or re-scoped:
- Sync relevant `.codex/agents/*.toml` files.
- Sync README skill catalogs and install guidance.
- Sync QUICKSTART copy commands.
- Sync templates if agent routing, handoffs, or recommended usage changed.

When workflows change:
- Keep YAML high-level and outcome-oriented.
- Put detailed operational procedures in skills, not in workflow files.
- Do not encode role definitions inside workflow steps.

## Repository-Specific Guidance

- Keep `project-conventions` aligned with the actual stack contract; it should refine `stack/default-stack.yaml`, not contradict it.
- Keep `code-review` as the default read-only review skill. Optional automation such as `codex-review-loop` should extend the template, not silently replace the default review path.
- If install surface changes, verify that partial-install commands remain copy-paste safe for backend-only and frontend-only setups.
