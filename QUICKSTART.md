# Quickstart

This repository is meant to be copied or vendored into another project so teams can reuse:
- stack-aware skills
- official Codex subagents
- official Codex skill directories
- stack and workflow support files

This repository now follows the official Codex layout:

```text
.codex/agents/*.toml
.agents/skills/*/SKILL.md
```

## Recommended: Install Into A Project

From this repository, copy the official Codex layer directly:

```sh
cp -R .codex .agents stack workflows /absolute/path/to/your-project/
```

This copies:
- `.codex/`
- `.agents/`
- `stack/`
- `workflows/`

into the target project.

Then add the project-level `AGENTS.md` template:

```sh
cp templates/project-AGENTS.md /absolute/path/to/your-project/AGENTS.md
```

The result looks like:

```text
your-project/
  AGENTS.md
  .codex/
    config.toml
    agents/
      backend_implementer.toml
      db_migration_owner.toml
      devops_release_owner.toml
      frontend_data_validation_implementer.toml
      frontend_implementer.toml
      frontend_ui_implementer.toml
      integration_contract_keeper.toml
      qa_debugger.toml
      reviewer_guard.toml
      tech_lead_orchestrator.toml
  .agents/
    skills/
      ...
  stack/
  workflows/
```

Then open that project in Codex. Codex can discover:
- project subagents in `.codex/agents/`
- project skills in `.agents/skills/`

The bundled frontend skill pack in this template is curated for `Vue 3` and `Pinia`. The frontend skills are taken from `antfu/skills` and then adapted locally to this repository's role and workflow model. The optional `codex-review-loop` skill remains available for deeper review workflows.

## Backend-Only Install

If the target project is backend-only, install just the backend-oriented layer:

```sh
TARGET=/absolute/path/to/your-project
mkdir -p "$TARGET/.codex/agents" "$TARGET/.agents/skills"
cp .codex/config.toml "$TARGET/.codex/config.toml"
cp .codex/agents/{backend_implementer.toml,db_migration_owner.toml,devops_release_owner.toml,qa_debugger.toml,reviewer_guard.toml,tech_lead_orchestrator.toml} "$TARGET/.codex/agents/"
cp -R .agents/skills/{agent-browser,api-contracts,backend-dtos,backend-exceptions,backend-feature,backend-logging,backend-structure,code-review,codex-review-loop,db-migration,devops-release,dishka-di,fastapi-controllers,project-conventions,repo-intake,service-layer,sqlalchemy-repositories,task-decomposition,test-debug,unit-of-work} "$TARGET/.agents/skills/"
cp -R stack "$TARGET/"
cp templates/project-AGENTS.backend.md "$TARGET/AGENTS.md"
```

This partial install intentionally skips `workflows/`, because the bundled workflow files assume the full multi-agent role set.

## Frontend-Only Install

If the target project is frontend-only, install just the frontend-oriented layer:

```sh
TARGET=/absolute/path/to/your-project
mkdir -p "$TARGET/.codex/agents" "$TARGET/.agents/skills"
cp .codex/config.toml "$TARGET/.codex/config.toml"
cp .codex/agents/{frontend_data_validation_implementer.toml,frontend_implementer.toml,frontend_ui_implementer.toml,qa_debugger.toml,reviewer_guard.toml,tech_lead_orchestrator.toml} "$TARGET/.codex/agents/"
cp -R .agents/skills/{agent-browser,code-review,codex-review-loop,frontend-data-access,frontend-feature,frontend-forms-and-validation,frontend-structure,pinia,project-conventions,repo-intake,task-decomposition,test-debug,vue,web-design-guidelines} "$TARGET/.agents/skills/"
cp -R stack "$TARGET/"
cp templates/project-AGENTS.frontend.md "$TARGET/AGENTS.md"
```

This partial install also skips `workflows/`, because the bundled workflow files assume the full multi-agent role set.

If you want adversarial PR or branch reviews through Codex CLI, keep `.agents/skills/codex-review-loop`.

## Optional: Install `agent-browser` CLI

If you plan to run browser automation flows locally, install the CLI separately:

```sh
npm install -g agent-browser && agent-browser install
```

## Optional: Install Skills Globally

If you want the skills available outside one project, copy them into your home-level Codex skill directory:

```sh
mkdir -p "$HOME/.agents/skills"
cp -R .agents/skills/* "$HOME/.agents/skills/"
```

This makes the skills available in:

```text
$HOME/.agents/skills/
```

## Notes

- If the target project already has `.codex/` or `.agents/`, merge carefully instead of blindly overwriting files.
- If the target project already has `AGENTS.md`, merge carefully instead of overwriting it blindly.
- Official docs:
  - https://developers.openai.com/codex/subagents
  - https://developers.openai.com/codex/skills
- The target stack assumptions are documented in `stack/default-stack.yaml`.
