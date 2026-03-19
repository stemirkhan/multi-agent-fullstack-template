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

The result looks like:

```text
your-project/
  .codex/
    config.toml
    agents/
      backend_implementer.toml
      db_migration_owner.toml
      devops_release_owner.toml
      frontend_implementer.toml
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
- Official docs:
  - https://developers.openai.com/codex/subagents
  - https://developers.openai.com/codex/skills
- The target stack assumptions are documented in `stack/default-stack.yaml`.
