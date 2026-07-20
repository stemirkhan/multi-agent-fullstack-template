# Quickstart

This repository installs project-scoped Codex agents, skills, stack guidance,
and profile-specific workflows into an existing project. Installation is driven by the
declarative profiles in `distribution/profiles.toml`.

## Requirements

- Python 3.12, 3.13, or 3.14. The installer is standard-library-only; source
  integrity checks additionally use `requirements-validation.txt`.
- Linux or macOS for applying an install: overwrite protection and rollback use
  POSIX `dir_fd`, no-follow, and hard-link semantics.
- A local checkout of this repository.
- A target project directory that you are prepared to modify.

## Choose A Profile

| Profile | Includes |
| --- | --- |
| `full` | Backend, frontend, contract, migration, release, QA, review, stack, and workflows |
| `backend` | Backend-oriented agents, skills, and backend-only workflows |
| `frontend` | Frontend-oriented agents, skills, API-contract guidance, and frontend-only workflows |

Partial profiles are transitively validated: copied agents cannot require a
skill or workflow that the profile omits.

## Preview The Install

Always start with a dry run:

```bash
python3 scripts/install.py \
  --profile full \
  --target /absolute/path/to/your-project \
  --dry-run
```

Replace `full` with `backend` or `frontend` as needed. The preview lists every
destination and reports conflicts without changing the target.

## Apply The Install

```bash
python3 scripts/install.py \
  --profile full \
  --target /absolute/path/to/your-project
```

The installer refuses to overwrite an existing file. Review conflicts and
merge project-owned instructions deliberately. Use `--force` only when you
intend to replace every reported destination:

```bash
python3 scripts/install.py \
  --profile full \
  --target /absolute/path/to/your-project \
  --force
```

After a full install, the target contains:

```text
your-project/
  AGENTS.md
  .codex/
    config.toml
    agents/
      ...
  .agents/
    skills/
      ...
  stack/
    default-stack.yaml
  workflows/
    ...
```

Backend and frontend profiles install profile-specific workflows containing
only available roles. Their agents still discover installed roles before
delegating and load task-specific skills conditionally.

## Customize The Target Project

Open the installed `AGENTS.md` and record the target project's real:

- bootstrap and development commands;
- lint, formatting, type-check, and test commands;
- backend/frontend entrypoints and generated artifacts;
- migration command and isolated test-database safeguard;
- build, release, and rollback commands where applicable.

Do not leave invented placeholder commands in project guidance.

## Optional Browser Automation

The `agent-browser` skill is included where the profile declares it, but its CLI
is a separate dependency. Install it only when browser-driven verification is
needed:

```bash
npm install -g agent-browser
agent-browser install
```

Agents should use browser automation only when `command -v agent-browser`
succeeds; otherwise they must fall back to code-level or manual verification.

## User-Scoped Skills

Do not bulk-copy this catalog into `$HOME/.agents/skills`: several skills rely
on project-scoped stack, convention, or review assets. Use the supported project
profiles, or install an individually reviewed self-contained skill separately.

## Validate The Source Template

Before publishing changes to this repository, run:

```bash
python3 -m pip install --requirement requirements-validation.txt
bash scripts/check-integrity.sh
python3 -m unittest discover -s tests -v
```

The checks parse TOML, YAML, and the review JSON schema; validate stack and
workflow shapes, documentation catalogs, local references, and profile closure;
and exercise transactional installer behavior plus smoke installs for every
profile.

## Notes

- Applied installs roll back handled copy and filesystem errors. They are not
  crash-consistent across `SIGKILL`, host failure, or power loss.
- Project `.codex/config.toml` is loaded only for a trusted project.
- Reusable agent files intentionally inherit the parent model rather than
  pinning an entitlement-specific model id.
- The architecture contract lives in `stack/default-stack.yaml`.
- Official references: [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Build skills](https://learn.chatgpt.com/docs/build-skills), and [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
