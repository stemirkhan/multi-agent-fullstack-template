---
name: repo-intake
description: Use when starting work in an unfamiliar repository to inventory the stack, commands, entrypoints, constraints, and ownership boundaries before making changes.
---

# Repo Intake

Use this skill before substantial work in an unfamiliar repository or package.

## Goals

- Identify the actual stack, not the assumed one.
- Find the entrypoints, commands, tests, and ownership boundaries that matter for the task.
- Surface constraints early so implementation does not start from false assumptions.

## Default Discovery Sequence

1. Read the top-level layout and identify major apps, packages, and tooling.
2. Find project entrypoints and run commands: build, test, lint, dev, migrations.
3. Inspect dependency manifests and framework-specific config.
4. Find architecture anchors: API layer, service layer, persistence layer, UI layer, shared contracts.
5. Find test locations and how they map to changed code.
6. Find any local conventions, AGENTS docs, or stack manifests in the repo.

## What To Inspect First

- `README`, `AGENTS`, package manifests, lockfiles, task runners, and CI configs.
- Backend app factory, routing setup, DI wiring, model and migration directories.
- Frontend app entry, routing, component system, data-access layer, and form patterns.
- Test commands and representative tests close to the target area.

## Heuristics

- Prefer existing local patterns over generic best practices when the repo is already opinionated.
- Distinguish shared infrastructure from feature-local code.
- Look for generated code and contract pipelines before editing generated artifacts directly.
- Verify whether the repo is a monolith, monorepo, or split app/package layout.

## Output Contract

Return:
- relevant apps or packages
- key commands to run
- affected ownership boundaries
- important conventions discovered
- risks or unknowns that could change the implementation plan
