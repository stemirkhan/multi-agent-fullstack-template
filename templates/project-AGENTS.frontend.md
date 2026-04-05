# Frontend Project Instructions

This file is meant to be copied into a frontend-focused target project as `AGENTS.md`.

## Purpose

- Define project-local operating instructions for Codex and Codex subagents.
- Point Codex at the installed `.codex/agents/`, `.agents/skills/`, and `stack/` layers.
- Keep frontend implementation, debugging, browser verification, and review consistent.

## Default Agent Routing

- Use `tech_lead_orchestrator` first when the task spans multiple files, layers, or agents.
- Use `frontend_ui_implementer` for Vue and Nuxt presentation work: components, layouts, styling, accessibility, and responsive behavior.
- Use `frontend_data_validation_implementer` for typed API access, Nuxt async-data flows, Pinia state, forms, and schema-driven validation.
- Use `frontend_implementer` only for small frontend tasks that are too coupled to split safely.
- Use `qa_debugger` for reproduction, failing paths, regression checks, and browser-heavy verification.
- Use `reviewer_guard` for final review, release-blocking findings, and missing-test analysis.

## Stack Contract

Follow `stack/default-stack.yaml` unless the task explicitly changes the architecture.

Frontend defaults:
- TypeScript-first Vue with Nuxt 3.
- Keep pages and layouts thin.
- Put reusable behavior in composables.
- Use Pinia only for shared client state that truly crosses routes or features.
- Keep typed API access in dedicated data-access seams.
- Keep forms schema-driven and backend error mapping explicit.

## Browser Automation

- If `agent-browser` is installed, use it for browser-heavy reproduction, screenshots, scraping, downloads, and login-driven UI verification.
- Keep browser automation in `qa_debugger` by default, or in frontend agents for targeted UI verification.

## Expected Handoffs

When using multiple subagents, return:
- changed files
- tests run
- residual risks
- clear ownership for any follow-up work
