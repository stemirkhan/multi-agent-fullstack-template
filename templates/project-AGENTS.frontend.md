# Frontend Project Instructions

This file is meant to be copied into a frontend-focused target project as
`AGENTS.md` and then completed with that project's exact commands and entrypoints.

## Purpose

- Define project-local operating instructions for Codex and Codex subagents.
- Point Codex at the installed `.codex/agents/`, `.agents/skills/`, and `stack/` layers.
- Keep frontend implementation, debugging, browser verification, and review consistent.

## Default Agent Routing

- Use `tech_lead_orchestrator` first when the task spans multiple files, layers, or agents.
- Use `frontend_ui_implementer` for Vue presentation work: components, route views, app shell, styling, accessibility, and responsive behavior.
- Use `frontend_data_validation_implementer` for typed API access, composable-driven data flows, Pinia state, forms, and schema-driven validation.
- Use `frontend_implementer` only for small frontend tasks that are too coupled to split safely.
- Use `qa_debugger` for reproduction, failing paths, regression checks, and browser-heavy verification.
- Use `reviewer_guard` for final review, release-blocking findings, and missing-test analysis.
- Before delegating, discover the agents actually installed under `.codex/agents/`; never route work to an unavailable role.

## Workflow Usage

- Prefer the installed frontend profile workflows for feature delivery, bugfixes, and refactors.
- Treat workflows as sequencing and handoff contracts, not role definitions.
- Confirm every workflow role exists under `.codex/agents/` before execution.

## UI And Product Copy

- Load `antislop` when installed and relevant to UI creation or refinement, or product copy; preserve the existing design system and user scope.
- For reviews, load it only when visual or copy quality is explicitly in scope; keep reviews read-only and prioritize correctness.

## Stack Contract

Follow `stack/default-stack.yaml` unless the task explicitly changes the architecture.

Frontend defaults:
- TypeScript-first Vue 3.
- Keep route views and screen-level entry components thin.
- Put reusable behavior in composables.
- Keep server state, request status, refresh, and invalidation in typed data-access/query seams.
- Use Pinia only for shared client-owned state that truly crosses features or views; keep transient presentation and form state local.
- Keep typed API access in dedicated data-access seams.
- Keep forms schema-driven and backend error mapping explicit.
- Keep emitted OpenAPI/client types aligned and treat route, status, header, auth, and documented error changes as contract changes.
- Keep secrets and privileged policy out of client code; handle tokens, cookies, storage, and untrusted content deliberately.

## Operating Procedure

- Before editing, choose the intended landing zone and decide whether structural prep is required first.
- If a task changes both structure and behavior, decompose it into at least two phases: structural prep first, then feature work.
- If a view, composable, store, or data-access seam starts serving a second unrelated feature family, split it before adding more behavior.
- If implementation discovers boundary widening, a wrong landing zone, or an unplanned external dependency family or cross-boundary capability seam, stop and route the work back through orchestration before continuing.
- Handoffs should record the chosen landing zone, whether structural prep was required or deferred, and any important boundary exceptions taken.

## Project-Specific Commands

- Record the real bootstrap, development, lint, type-check, unit-test, browser-test, and build commands before relying on automation.
- Record the application entrypoint, router/runtime mode, generated API client artifacts, and design-system location.
- Do not invent a missing command. Discover it from project manifests or ask the maintainer to document it.

## Browser Automation

- If the `agent-browser` CLI is available (`command -v agent-browser`), use it for browser-heavy reproduction, screenshots, scraping, downloads, and login-driven UI verification.
- Keep browser automation in `qa_debugger` by default, or in frontend agents for targeted UI verification.

## Expected Handoffs

When using multiple subagents, return:
- summary
- changed files
- tests run
- residual risks
- open questions and the owner of each follow-up
- clear ownership for any follow-up work
