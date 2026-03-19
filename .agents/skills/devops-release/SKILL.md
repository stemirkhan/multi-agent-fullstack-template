---
name: devops-release
description: Use when working on CI, CD, containers, infrastructure, deployment configuration, rollout plans, rollback procedures, or runtime observability for the Python backend and TypeScript frontend stack.
---

# DevOps Release

Use this skill when the task touches delivery pipelines, deployment safety, runtime config, or operational observability.

## Responsibilities

- Keep backend and frontend delivery safe, reproducible, and observable.
- Make rollout, rollback, and environment assumptions explicit.
- Catch config drift and operational risk before release.

## Default Workflow

1. Identify the services, apps, jobs, or infra surfaces affected.
2. Identify the environment path: local, CI, preview, staging, production.
3. Check build, test, migration, and artifact assumptions for both backend and frontend.
4. Decide rollout order, especially if schema, background jobs, or shared contracts changed.
5. Define rollback or fallback behavior before deployment.
6. Verify observability, health checks, and runtime config changes.

## Rules

- Prefer reversible rollout steps.
- Keep app deploys, schema changes, and config flips coordinated but not silently coupled.
- Treat secrets, environment variables, and runtime feature flags as part of the release contract.
- Do not assume frontend-only changes are risk-free if they depend on backend contract or caching behavior.
- Do not assume backend-only changes are isolated if generated clients, edge config, or frontend data hooks depend on them.

## CI And CD Guidance

- Ensure the pipeline runs the smallest meaningful set of checks for the changed surfaces.
- Keep migration steps explicit in CI or deployment automation when required.
- Prefer deterministic build artifacts and pinned toolchain behavior where possible.
- If preview or staging deploys exist, use them to validate contract and env assumptions before production.

## Rollout Guidance

- For schema-affecting releases, prefer: expand schema -> deploy compatible backend -> deploy frontend or workers -> enforce stricter constraints later.
- For risky feature work, prefer feature flags or staged rollout when available.
- For frontend changes, verify cache, asset, and environment configuration behavior after deployment.
- For backend changes, verify health endpoints, startup behavior, migrations, and background processes.

## Rollback Guidance

- Define whether rollback means artifact rollback, config rollback, database downgrade, or operational fallback.
- Be explicit when database changes are not safely reversible.
- If rollback depends on compatibility windows, document that window clearly.
- Prefer a known fallback path over improvising during an incident.

## Operational Verification

- health checks
- logs and error rates
- key business flows
- background job behavior
- migration status
- environment variables and secrets presence
- frontend asset delivery and API connectivity

## Handoff

Return:
- environments affected
- pipeline or infra changes
- rollout and rollback plan
- migration or contract dependencies
- post-deploy verification checks
