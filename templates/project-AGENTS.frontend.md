# Frontend Project Instructions

This file is meant to be copied into a frontend-focused target project as `AGENTS.md`.

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

## Stack Contract

Follow `stack/default-stack.yaml` unless the task explicitly changes the architecture.

Frontend defaults:
- TypeScript-first Vue 3.
- Keep route views and screen-level entry components thin.
- Put reusable behavior in composables.
- Use Pinia only for shared client state that truly crosses features or views.
- Keep typed API access in dedicated data-access seams.
- Keep forms schema-driven and backend error mapping explicit.

## Operating Procedure

- Before editing, choose the intended landing zone and decide whether structural prep is required first.
- If a task changes both structure and behavior, decompose it into at least two phases: structural prep first, then feature work.
- If a view, composable, store, or data-access seam starts serving a second unrelated feature family, split it before adding more behavior.
- If implementation discovers boundary widening, a wrong landing zone, or an unexpected new dependency family, stop and route the work back through orchestration before continuing.
- Handoffs should record the chosen landing zone, whether structural prep was required or deferred, and any important boundary exceptions taken.

## Browser Automation

- If `agent-browser` is installed, use it for browser-heavy reproduction, screenshots, scraping, downloads, and login-driven UI verification.
- Keep browser automation in `qa_debugger` by default, or in frontend agents for targeted UI verification.

## Expected Handoffs

When using multiple subagents, return:
- changed files
- tests run
- residual risks
- clear ownership for any follow-up work
