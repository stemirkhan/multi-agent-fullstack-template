# Repository Conventions

This repository stores reusable multi-agent scaffolding for fullstack development.

Rules:
- Keep canonical role definitions in `agents/roles/`.
- Keep copy-ready official Codex subagents in `.codex/agents/`.
- Keep official Codex skills in `.agents/skills/`.
- Keep skills vendor-agnostic unless a Codex-specific behavior is unavoidable.
- Keep each `.agents/skills/*/SKILL.md` concise; move detailed procedures into bundled resources later.
- Treat workflows as sequencing and handoff contracts, not as role definitions.
- Prefer adding new roles only when ownership boundaries are materially different.
- Treat `stack/default-stack.yaml` as the default architectural contract when creating or refining skills.
- For backend assumptions, prefer FastAPI controllers, service layer orchestration, Unit of Work transaction control, repositories, DTOs, explicit exceptions, and structured logging.
- For frontend assumptions, prefer TypeScript React with `shadcn/ui`, `Radix UI`, `Tailwind CSS`, `TanStack Query`, `React Hook Form`, and `Zod`.
