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

- Split by layer when responsibilities are already distinct: backend, frontend, contracts, migrations, review.
- Split by write scope when multiple agents would otherwise touch the same files.
- Keep tightly coupled, short tasks together if splitting would create overhead without reducing risk.
- Separate migration or rollout work when schema or infrastructure changes are involved.
- Add a reviewer or debugger pass when the blast radius is high.

## Ownership Rules

- One clear owner per write scope.
- Shared contracts should have an explicit owner, not “everyone touches it”.
- Reviewers are read-only unless explicitly reassigned to patch.
- Migration and devops changes deserve dedicated ownership when production risk exists.

## Dependency Mapping

- Contracts before consumers when shapes change.
- Service or domain behavior before transport mapping when backend logic changes.
- Schema expansion before app rollout when database compatibility matters.
- Data-access hooks before UI composition when the frontend depends on changed server state.

## Work Packet Format

Each packet should include:
- goal
- owned files or areas
- required inputs
- expected outputs
- dependencies
- validation or tests

## Handoff Rules

- Handoffs should name changed files, contract assumptions, tests run, and residual risks.
- Do not hand off vague statements like “backend done”.
- Escalate when two packets need the same write scope or when acceptance criteria conflict.

## Output Contract

Return:
- execution plan
- ownership map
- dependency order
- handoff expectations
- open risks
