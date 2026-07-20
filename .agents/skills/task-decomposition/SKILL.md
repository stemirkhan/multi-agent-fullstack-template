---
name: task-decomposition
description: Use when a request needs to be split across multiple specialized subagents with explicit ownership, handoffs, dependencies, and acceptance criteria.
---

# Task Decomposition

Use this skill when one request should be broken into separate work packets instead of handled as one undifferentiated task.

## Goals

- Split work along real ownership and risk boundaries.
- Minimize merge conflicts and duplicated effort.
- Make dependencies and handoffs explicit before implementation starts.

## Decomposition Heuristics

- Split by layer when responsibilities are already distinct: backend, contracts, migrations, review.
- Split by write scope when multiple agents would otherwise touch the same files.
- Keep tightly coupled, short tasks together if splitting would create overhead without reducing risk.
- Separate migration or rollout work when schema or infrastructure changes are involved.
- Add a reviewer or debugger pass when the blast radius is high.
- When the target file is already overloaded, add a structural-prep packet first so the feature lands in the right module shape.
- When a broad UoW, repository, or service already spans multiple capability families, create a structural-prep packet first to extract family ports, landing zones, or compatibility facades before behavior work.
- Do not split a cohesive end-to-end backend feature merely because it touches controller, service, port, and infrastructure layers; split when separate ownership, sequencing, or risk control provides a concrete benefit.

## Ownership Rules

- One clear owner per write scope.
- Shared contracts should have an explicit owner, not “everyone touches it”.
- Reviewers are read-only unless explicitly reassigned to patch.
- Migration and devops changes deserve dedicated ownership when production risk exists.
- In scaffolding repos, keep canonical Codex role instructions in `.codex/agents`, reusable implementation guidance in the shared skills layer, and sequencing in the workflow layer.

## Dependency Mapping

- Contracts before consumers when shapes change.
- Service or domain behavior before transport mapping when backend logic changes.
- Schema expansion before app rollout when database compatibility matters.
- API contract changes before service consumers when shared shapes change.
- Canonical `.codex/agents` updates before workflow routing changes when scaffolding ownership changes.
- Compatibility facade creation before broad import migration when splitting a shared module.
- Port extraction and landing-zone choice before feature logic when boundary direction or dependency shape is changing.
- Do not classify expected DTO, repository, controller, or wiring work in an already planned end-to-end feature as boundary widening.

## Work Packet Format

Each packet should include:
- goal
- owned files or areas
- chosen landing zone
- required inputs
- expected outputs
- allowed boundary crossings
- dependencies
- validation or tests

## Handoff Rules

- Handoffs should name changed files, contract assumptions, tests run, and residual risks.
- Do not hand off vague statements like “backend done”.
- Escalate when two packets need the same write scope or when acceptance criteria conflict.
- If implementation discovers an unplanned dependency direction change, new capability family, or wrong landing zone, pause that branch and add a structural-prep packet before continuing behavior work.

## Output Contract

Return:
- execution plan
- ownership map
- dependency order
- handoff expectations
- open risks
