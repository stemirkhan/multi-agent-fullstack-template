#!/usr/bin/env python3
"""Validate the template source and every declared distribution profile."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import runpy
import tomllib
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # Reported as an integrity issue by validate_repository.
    yaml = None  # type: ignore[assignment]

YAML_PARSE_ERRORS = (RuntimeError,) if yaml is None else (RuntimeError, yaml.YAMLError)

from distribution_lib import (
    DistributionError,
    PROFILE_AGENT_TEMPLATES,
    REQUIRED_PROFILES,
    REQUIRED_WORKFLOW_IDS,
    build_profile_plan,
    load_manifest,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AGENT_REQUIRED_FIELDS = ("name", "description", "developer_instructions")
AGENT_ALLOWED_FIELDS = {
    "name",
    "description",
    "nickname_candidates",
    "model",
    "model_reasoning_effort",
    "sandbox_mode",
    "developer_instructions",
}
READ_ONLY_AGENTS = {"reviewer_guard", "tech_lead_orchestrator"}
REASONING_EFFORTS = {"minimal", "low", "medium", "high", "xhigh"}
REQUIRED_WORKFLOW_SECTIONS = ("sequence", "done_when", "error_handling")
CODE_SPAN_PATTERN = re.compile(r"`([^`\n]+)`")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]\n]+\]\(([^)\n]+)\)")
ROOT_REFERENCE_PREFIXES = (".agents/", "stack/", "workflows/")
SKILL_REFERENCE_PREFIXES = ("scripts/", "references/", "templates/", "assets/")
STACK_PATH = Path("stack/default-stack.yaml")
REVIEW_SCHEMA_PATH = Path(
    ".agents/skills/codex-review-loop/references/schemas/review-findings.schema.json"
)
REVIEW_SCHEMA_VALIDATOR_PATH = Path(
    ".agents/skills/codex-review-loop/scripts/validate-review-output.py"
)


if yaml is not None:
    class _UniqueKeySafeLoader(yaml.SafeLoader):
        """Safe YAML loader that rejects duplicate mapping keys."""


    def _construct_unique_mapping(
        loader: _UniqueKeySafeLoader,
        node: yaml.MappingNode,
        deep: bool = False,
    ) -> dict[Any, Any]:
        loader.flatten_mapping(node)
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable mapping key",
                    key_node.start_mark,
                ) from exc
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping


    _UniqueKeySafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        _construct_unique_mapping,
    )


@dataclass(frozen=True, order=True)
class Issue:
    path: str
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}"


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _read_text(root: Path, path: Path, issues: list[Issue]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        issues.append(Issue(_display_path(root, path), f"cannot read UTF-8 text: {exc}"))
        return None


def _load_toml(root: Path, path: Path, issues: list[Issue]) -> dict[str, Any] | None:
    try:
        with path.open("rb") as stream:
            return tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        issues.append(Issue(_display_path(root, path), f"invalid TOML: {exc}"))
        return None


def _parse_yaml(text: str) -> Any:
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required; install requirements-validation.txt"
        )
    return yaml.load(text, Loader=_UniqueKeySafeLoader)


def _load_yaml(root: Path, path: Path, issues: list[Issue]) -> Any | None:
    text = _read_text(root, path, issues)
    if text is None:
        return None
    try:
        return _parse_yaml(text)
    except YAML_PARSE_ERRORS as exc:
        message = str(exc) if isinstance(exc, RuntimeError) else f"invalid YAML: {exc}"
        issues.append(Issue(_display_path(root, path), message))
    return None


def _require_mapping(
    value: Any,
    display: str,
    label: str,
    issues: list[Issue],
) -> dict[str, Any] | None:
    if not isinstance(value, dict) or not all(
        isinstance(key, str) for key in value
    ):
        issues.append(Issue(display, f"{label} must be a mapping with string keys"))
        return None
    return value


def _require_nonempty_string(
    mapping: dict[str, Any],
    key: str,
    display: str,
    label: str,
    issues: list[Issue],
) -> str | None:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        issues.append(Issue(display, f"{label}.{key} must be a non-empty string"))
        return None
    return value


def _require_string_list(
    mapping: dict[str, Any],
    key: str,
    display: str,
    label: str,
    issues: list[Issue],
) -> list[str] | None:
    value = mapping.get(key)
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        issues.append(
            Issue(display, f"{label}.{key} must be a non-empty list of strings")
        )
        return None
    return value


def extract_read_before(text: str) -> tuple[str, ...]:
    references: list[str] = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if "read before acting" in stripped.lower():
            in_block = True
            continue
        if not in_block:
            continue
        if not stripped:
            break
        match = re.match(r"^-\s+(.+?)\s*$", stripped)
        if match:
            references.append(match.group(1))
    return tuple(references)


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


def extract_skill_references(text: str) -> tuple[tuple[str, bool], ...]:
    references: set[tuple[str, bool]] = set()
    candidates = CODE_SPAN_PATTERN.findall(text) + MARKDOWN_LINK_PATTERN.findall(text)
    for value in candidates:
        candidate = value.strip().strip("<>").split("#", 1)[0].rstrip(".,:;")
        if not candidate or any(character.isspace() for character in candidate):
            continue
        if any(character in candidate for character in "*?{}$<>"):
            continue
        if candidate == "AGENTS.md" or candidate.startswith(ROOT_REFERENCE_PREFIXES):
            references.add((candidate, True))
        elif candidate.startswith(SKILL_REFERENCE_PREFIXES):
            references.add((candidate, False))
    return tuple(sorted(references))


def _destination_is_present(destinations: set[Path], reference: Path) -> bool:
    return reference in destinations or any(
        destination.is_relative_to(reference) for destination in destinations
    )


def parse_workflow(text: str) -> tuple[str | None, tuple[str, ...]]:
    try:
        data = _parse_yaml(text)
    except YAML_PARSE_ERRORS:
        return None, ()
    if not isinstance(data, dict):
        return None, ()
    workflow_id = data.get("id")
    sequence = data.get("sequence")
    roles = tuple(
        step["role"]
        for step in sequence
        if isinstance(step, dict) and isinstance(step.get("role"), str)
    ) if isinstance(sequence, list) else ()
    return (workflow_id if isinstance(workflow_id, str) else None, roles)


def missing_workflow_sections(text: str) -> tuple[str, ...]:
    try:
        data = _parse_yaml(text)
    except YAML_PARSE_ERRORS:
        return REQUIRED_WORKFLOW_SECTIONS
    if not isinstance(data, dict):
        return REQUIRED_WORKFLOW_SECTIONS
    return tuple(section for section in REQUIRED_WORKFLOW_SECTIONS if section not in data)


def _validate_workflow_shape(
    data: Any,
    display: str,
    issues: list[Issue],
) -> tuple[str | None, tuple[str, ...]]:
    workflow = _require_mapping(data, display, "workflow", issues)
    if workflow is None:
        return None, ()

    allowed_workflow_keys = {"id", "goal", "sequence", "done_when", "error_handling"}
    unexpected_workflow_keys = set(workflow) - allowed_workflow_keys
    if unexpected_workflow_keys:
        issues.append(
            Issue(
                display,
                "workflow contains unsupported fields: "
                f"{', '.join(sorted(unexpected_workflow_keys))}",
            )
        )

    workflow_id = _require_nonempty_string(
        workflow, "id", display, "workflow", issues
    )
    _require_nonempty_string(workflow, "goal", display, "workflow", issues)

    roles: list[str] = []
    sequence = workflow.get("sequence")
    if "sequence" not in workflow:
        issues.append(Issue(display, "workflow section is missing: sequence"))
    elif not isinstance(sequence, list) or not sequence:
        issues.append(Issue(display, "workflow.sequence must be a non-empty list"))
    else:
        for index, step_value in enumerate(sequence):
            label = f"workflow.sequence[{index}]"
            step = _require_mapping(step_value, display, label, issues)
            if step is None:
                continue
            allowed_step_keys = {"role", "output", "phase", "optional_when"}
            unexpected_step_keys = set(step) - allowed_step_keys
            if unexpected_step_keys:
                issues.append(
                    Issue(
                        display,
                        f"{label} contains unsupported fields: "
                        f"{', '.join(sorted(unexpected_step_keys))}",
                    )
                )
            role = _require_nonempty_string(step, "role", display, label, issues)
            _require_nonempty_string(step, "output", display, label, issues)
            if role is not None:
                roles.append(role)
            for optional_key in ("phase", "optional_when"):
                if optional_key in step:
                    _require_nonempty_string(
                        step, optional_key, display, label, issues
                    )

    if "done_when" not in workflow:
        issues.append(Issue(display, "workflow section is missing: done_when"))
    else:
        _require_string_list(workflow, "done_when", display, "workflow", issues)
    error_handling = workflow.get("error_handling")
    if "error_handling" not in workflow:
        issues.append(Issue(display, "workflow section is missing: error_handling"))
    elif not isinstance(error_handling, dict) or not error_handling:
        issues.append(
            Issue(display, "workflow.error_handling must be a non-empty mapping")
        )
    else:
        for key, value in error_handling.items():
            if not isinstance(key, str) or not key.strip():
                issues.append(
                    Issue(display, "workflow.error_handling keys must be non-empty strings")
                )
            if not isinstance(value, str) or not value.strip():
                issues.append(
                    Issue(
                        display,
                        f"workflow.error_handling[{key!r}] must be a non-empty string",
                    )
                )
    return workflow_id, tuple(roles)


def _iter_yaml_strings(value: Any) -> Any:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _iter_yaml_strings(key)
            yield from _iter_yaml_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_yaml_strings(item)


def _validate_toml_files(root: Path, issues: list[Issue]) -> None:
    paths = sorted((root / ".codex").rglob("*.toml"))
    paths.extend(sorted((root / "distribution").rglob("*.toml")))
    for path in paths:
        _load_toml(root, path, issues)


def _validate_stack(root: Path, issues: list[Issue]) -> None:
    path = root / STACK_PATH
    data = _load_yaml(root, path, issues)
    if data is None:
        return
    display = STACK_PATH.as_posix()
    stack = _require_mapping(data, display, "stack", issues)
    if stack is None:
        return

    _require_nonempty_string(stack, "name", display, "stack", issues)
    metadata = _require_mapping(stack.get("metadata"), display, "stack.metadata", issues)
    if metadata is not None:
        schema_version = metadata.get("schema_version")
        if type(schema_version) is not int or schema_version != 1:
            issues.append(Issue(display, "stack.metadata.schema_version must be 1"))
        contract_version = metadata.get("contract_version")
        if (
            not isinstance(contract_version, int)
            or isinstance(contract_version, bool)
            or contract_version < 1
        ):
            issues.append(
                Issue(display, "stack.metadata.contract_version must be a positive integer")
            )
        for key in ("status", "source_of_truth", "version_policy"):
            _require_nonempty_string(metadata, key, display, "stack.metadata", issues)
        if metadata.get("source_of_truth") != STACK_PATH.as_posix():
            issues.append(
                Issue(
                    display,
                    f"stack.metadata.source_of_truth must be {STACK_PATH.as_posix()!r}",
                )
            )
        _require_string_list(
            metadata, "synchronization", display, "stack.metadata", issues
        )

    backend = _require_mapping(stack.get("backend"), display, "stack.backend", issues)
    if backend is not None:
        for key in ("language", "framework", "orm", "migrations", "dependency_injection"):
            _require_nonempty_string(backend, key, display, "stack.backend", issues)
        runtime = _require_mapping(
            backend.get("runtime"), display, "stack.backend.runtime", issues
        )
        if runtime is not None:
            _require_nonempty_string(runtime, "baseline", display, "stack.backend.runtime", issues)
            _require_string_list(runtime, "policies", display, "stack.backend.runtime", issues)
        validation = _require_mapping(
            backend.get("validation_and_settings"),
            display,
            "stack.backend.validation_and_settings",
            issues,
        )
        if validation is not None:
            _require_nonempty_string(
                validation, "library", display, "stack.backend.validation_and_settings", issues
            )
            _require_string_list(
                validation, "policies", display, "stack.backend.validation_and_settings", issues
            )
        async_execution = _require_mapping(
            backend.get("async_execution"),
            display,
            "stack.backend.async_execution",
            issues,
        )
        if async_execution is not None:
            _require_nonempty_string(
                async_execution, "mode", display, "stack.backend.async_execution", issues
            )
            _require_string_list(
                async_execution, "policies", display, "stack.backend.async_execution", issues
            )
        architecture = _require_mapping(
            backend.get("architecture"), display, "stack.backend.architecture", issues
        )
        if architecture is not None:
            for key in (
                "transport",
                "application",
                "transactions",
                "persistence",
                "contracts",
                "errors",
                "dependency_direction",
            ):
                _require_nonempty_string(
                    architecture, key, display, "stack.backend.architecture", issues
                )
            _require_string_list(
                architecture, "ports", display, "stack.backend.architecture", issues
            )
        testing = _require_mapping(
            backend.get("testing"), display, "stack.backend.testing", issues
        )
        if testing is not None:
            for key in ("unit", "integration", "api"):
                _require_nonempty_string(
                    testing, key, display, "stack.backend.testing", issues
                )
            _require_string_list(
                testing, "policies", display, "stack.backend.testing", issues
            )
        for key in ("security", "observability", "guardrails"):
            _require_string_list(backend, key, display, "stack.backend", issues)

    frontend = _require_mapping(stack.get("frontend"), display, "stack.frontend", issues)
    if frontend is not None:
        for key in (
            "language",
            "framework",
            "state_management",
            "styling",
            "data_access",
            "forms",
            "validation",
        ):
            _require_nonempty_string(frontend, key, display, "stack.frontend", issues)
        architecture = _require_mapping(
            frontend.get("architecture"), display, "stack.frontend.architecture", issues
        )
        if architecture is not None:
            for key in ("ui", "data_access", "composition", "typing"):
                _require_nonempty_string(
                    architecture, key, display, "stack.frontend.architecture", issues
                )
            state = _require_mapping(
                architecture.get("state"),
                display,
                "stack.frontend.architecture.state",
                issues,
            )
            if state is not None:
                for key in ("server", "client", "local"):
                    _require_nonempty_string(
                        state,
                        key,
                        display,
                        "stack.frontend.architecture.state",
                        issues,
                    )
        testing = _require_mapping(
            frontend.get("testing"), display, "stack.frontend.testing", issues
        )
        if testing is not None:
            for key in ("unit", "component", "flow"):
                _require_nonempty_string(
                    testing, key, display, "stack.frontend.testing", issues
                )
            _require_string_list(
                testing, "policies", display, "stack.frontend.testing", issues
            )
        for key in ("security", "observability", "guardrails"):
            _require_string_list(frontend, key, display, "stack.frontend", issues)

    api_contract = _require_mapping(
        stack.get("api_contract"), display, "stack.api_contract", issues
    )
    if api_contract is not None:
        for key in ("authority", "consumer"):
            _require_nonempty_string(
                api_contract, key, display, "stack.api_contract", issues
            )
        _require_string_list(
            api_contract, "policies", display, "stack.api_contract", issues
        )


def _config_references(config: dict[str, Any]) -> tuple[str, ...]:
    agents = config.get("agents", {})
    if not isinstance(agents, dict):
        return ()
    references: list[str] = []
    for value in agents.values():
        if isinstance(value, dict) and isinstance(value.get("config_file"), str):
            references.append(value["config_file"])
    return tuple(references)


def _validate_configs(root: Path, issues: list[Issue]) -> None:
    config_paths = {root / ".codex/config.toml"}
    manifest = _load_toml(root, root / "distribution/profiles.toml", issues)
    if manifest and isinstance(manifest.get("base_config"), str):
        config_paths.add(root / manifest["base_config"])

    for config_path in sorted(config_paths):
        config = _load_toml(root, config_path, issues)
        if config is None:
            continue
        display = _display_path(root, config_path)
        features = config.get("features")
        if not isinstance(features, dict) or features.get("multi_agent") is not True:
            issues.append(Issue(display, "features.multi_agent must be true"))
        agents_config = config.get("agents")
        if not isinstance(agents_config, dict):
            issues.append(Issue(display, "agents must be a configuration table"))
        else:
            for key in ("max_threads", "max_depth"):
                value = agents_config.get(key)
                if type(value) is not int or value < 1:
                    issues.append(
                        Issue(display, f"agents.{key} must be a positive integer")
                    )
            for role, value in agents_config.items():
                if isinstance(value, dict) and "config_file" in value:
                    issues.append(
                        Issue(
                            display,
                            "nested agents.*.config_file is not allowed; project agents "
                            f"are auto-discovered from .codex/agents (found {role!r})",
                        )
                    )
        for reference in _config_references(config):
            reference_path = Path(reference)
            if reference_path.is_absolute() or ".." in reference_path.parts:
                issues.append(
                    Issue(
                        display,
                        f"config_file is not a safe relative path: {reference}",
                    )
                )
                continue
            referenced_path = (config_path.parent / reference).resolve()
            if not referenced_path.is_file():
                issues.append(
                    Issue(
                        display,
                        f"config_file resolves to missing file: {reference}",
                    )
                )


def _validate_agents(
    root: Path,
    issues: list[Issue],
) -> tuple[dict[str, tuple[Path, dict[str, Any], tuple[str, ...]]], dict[str, str]]:
    agents: dict[str, tuple[Path, dict[str, Any], tuple[str, ...]]] = {}
    names_by_filename: dict[str, str] = {}
    for path in sorted((root / ".codex/agents").glob("*.toml")):
        data = _load_toml(root, path, issues)
        if data is None:
            continue
        display = _display_path(root, path)
        unexpected_fields = set(data) - AGENT_ALLOWED_FIELDS
        if unexpected_fields:
            issues.append(
                Issue(
                    display,
                    "unsupported agent fields: "
                    f"{', '.join(sorted(unexpected_fields))}",
                )
            )
        for field in AGENT_REQUIRED_FIELDS:
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(Issue(display, f"missing non-empty required field {field!r}"))
        if "model" in data:
            issues.append(
                Issue(display, "hard model pin is not allowed; inherit the parent model")
            )

        nicknames = data.get("nickname_candidates")
        if (
            not isinstance(nicknames, list)
            or not nicknames
            or not all(
                isinstance(value, str) and value.strip() for value in nicknames
            )
            or len(nicknames) != len(set(nicknames))
        ):
            issues.append(
                Issue(
                    display,
                    "nickname_candidates must be a non-empty list of unique strings",
                )
            )
        reasoning_effort = data.get("model_reasoning_effort")
        if reasoning_effort not in REASONING_EFFORTS:
            issues.append(
                Issue(
                    display,
                    "model_reasoning_effort must be one of "
                    f"{sorted(REASONING_EFFORTS)}",
                )
            )

        name = data.get("name")
        instructions = data.get("developer_instructions")
        if not isinstance(name, str) or not name.strip():
            continue
        if name != path.stem:
            issues.append(
                Issue(
                    display,
                    f"agent name {name!r} must match filename stem {path.stem!r}",
                )
            )
        expected_sandbox = (
            "read-only" if name in READ_ONLY_AGENTS else "workspace-write"
        )
        if data.get("sandbox_mode") != expected_sandbox:
            issues.append(
                Issue(
                    display,
                    f"agent {name!r} sandbox_mode must be {expected_sandbox!r}",
                )
            )
        if name in agents:
            issues.append(Issue(display, f"duplicate agent name {name!r}"))
            continue
        references = extract_read_before(instructions) if isinstance(instructions, str) else ()
        agents[name] = (path, data, references)
        names_by_filename[path.stem] = name
        for reference in references:
            referenced_path = root / reference
            if not referenced_path.is_file():
                issues.append(Issue(display, f"Read before acting path is missing: {reference}"))

    if not agents:
        issues.append(Issue(".codex/agents", "no agent TOML files found"))
    return agents, names_by_filename


def _validate_skills(
    root: Path,
    issues: list[Issue],
) -> dict[str, tuple[Path, tuple[tuple[str, bool], ...]]]:
    skills: dict[str, tuple[Path, tuple[tuple[str, bool], ...]]] = {}
    for path in sorted((root / ".agents/skills").glob("*/SKILL.md")):
        text = _read_text(root, path, issues)
        if text is None:
            continue
        display = _display_path(root, path)
        frontmatter = _parse_frontmatter(text)
        if frontmatter is None:
            issues.append(Issue(display, "missing or malformed frontmatter"))
            continue
        name = frontmatter.get("name", "").strip()
        description = frontmatter.get("description", "").strip()
        if not name:
            issues.append(Issue(display, "frontmatter name is required"))
            continue
        if not description:
            issues.append(Issue(display, "frontmatter description is required"))
        if name != path.parent.name:
            issues.append(
                Issue(display, f"skill name {name!r} must match directory {path.parent.name!r}")
            )
        if name in skills:
            issues.append(Issue(display, f"duplicate skill name {name!r}"))
            continue

        references = extract_skill_references(text)
        skills[name] = (path.parent, references)
        for reference, from_root in references:
            referenced_path = root / reference if from_root else path.parent / reference
            if not referenced_path.exists():
                issues.append(Issue(display, f"local reference is missing: {reference}"))

    if not skills:
        issues.append(Issue(".agents/skills", "no SKILL.md files found"))
    return skills


def _validate_workflow_file(
    root: Path,
    path: Path,
    agent_names: set[str],
    issues: list[Issue],
) -> tuple[str | None, tuple[str, ...]]:
    data = _load_yaml(root, path, issues)
    if data is None:
        return None, ()
    display = _display_path(root, path)
    workflow_id, roles = _validate_workflow_shape(data, display, issues)
    for role in roles:
        if role not in agent_names:
            issues.append(Issue(display, f"workflow references unknown role {role!r}"))
    strings = tuple(_iter_yaml_strings(data))
    for agent_name in sorted(agent_names):
        legacy_alias = agent_name.replace("_", "-")
        alias_pattern = re.compile(
            rf"(?<![A-Za-z0-9_-]){re.escape(legacy_alias)}(?![A-Za-z0-9_-])"
        )
        if legacy_alias != agent_name and any(
            alias_pattern.search(value) for value in strings
        ):
            issues.append(
                Issue(
                    display,
                    f"workflow uses non-canonical role alias {legacy_alias!r}; use {agent_name!r}",
                )
            )
    return workflow_id, roles


def _validate_canonical_workflows(
    root: Path,
    agent_names: set[str],
    issues: list[Issue],
) -> None:
    workflow_ids: dict[str, Path] = {}
    paths = sorted((root / "workflows").glob("*.yaml"))
    if not paths:
        issues.append(Issue("workflows", "no canonical workflow YAML files found"))
        return
    for path in paths:
        workflow_id, _ = _validate_workflow_file(root, path, agent_names, issues)
        if workflow_id is None:
            continue
        if workflow_id != path.stem:
            issues.append(
                Issue(
                    _display_path(root, path),
                    f"workflow id {workflow_id!r} must match filename {path.stem!r}",
                )
            )
        if workflow_id in workflow_ids:
            issues.append(
                Issue(
                    _display_path(root, path),
                    f"duplicate canonical workflow id {workflow_id!r}",
                )
            )
        workflow_ids[workflow_id] = path

    actual_ids = set(workflow_ids)
    required_ids = set(REQUIRED_WORKFLOW_IDS)
    if actual_ids != required_ids:
        issues.append(
            Issue(
                "workflows",
                "canonical workflow ids mismatch; "
                f"missing={sorted(required_ids - actual_ids)}, "
                f"unexpected={sorted(actual_ids - required_ids)}",
            )
        )


def _relative_config_target(config_target: Path, reference: str) -> Path | None:
    candidate = config_target.parent / reference
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    return candidate


def _validate_profile(
    root: Path,
    profile_name: str,
    profile: dict[str, Any],
    config: dict[str, Any] | None,
    agents: dict[str, tuple[Path, dict[str, Any], tuple[str, ...]]],
    names_by_filename: dict[str, str],
    skills: dict[str, tuple[Path, tuple[tuple[str, bool], ...]]],
    issues: list[Issue],
) -> None:
    display = f"distribution/profiles.toml[{profile_name}]"
    try:
        operations = build_profile_plan(root, profile_name)
    except DistributionError as exc:
        issues.append(Issue(display, str(exc)))
        return

    destinations = {operation.destination for operation in operations}
    declared_agents = profile.get("agents", [])
    selected_names = {
        names_by_filename[name]
        for name in declared_agents
        if isinstance(name, str) and name in names_by_filename
    }
    template_relative = PROFILE_AGENT_TEMPLATES[profile_name]
    template_text = _read_text(root, root / template_relative, issues)
    if template_text is not None:
        referenced_names = {
            name
            for name in agents
            if re.search(
                rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])",
                template_text,
            )
        }
        if referenced_names != selected_names:
            issues.append(
                Issue(
                    display,
                    "project template agent catalog mismatch; "
                    f"missing={sorted(selected_names - referenced_names)}, "
                    f"omitted-profile-roles={sorted(referenced_names - selected_names)}",
                )
            )
    for filename in declared_agents:
        if isinstance(filename, str) and filename not in names_by_filename:
            issues.append(Issue(display, f"unknown agent file stem {filename!r}"))

    for name in selected_names:
        _, _, references = agents[name]
        for reference in references:
            if Path(reference) not in destinations:
                issues.append(
                    Issue(
                        display,
                        f"agent {name!r} requires omitted path {reference!r}",
                    )
                )

    declared_skills = profile.get("skills", [])
    for skill_name in declared_skills:
        if not isinstance(skill_name, str) or skill_name not in skills:
            issues.append(Issue(display, f"unknown skill {skill_name!r}"))
            continue
        _, references = skills[skill_name]
        for reference, from_root in references:
            destination = (
                Path(reference)
                if from_root
                else Path(f".agents/skills/{skill_name}") / reference
            )
            if not _destination_is_present(destinations, destination):
                issues.append(
                    Issue(
                        display,
                        f"skill {skill_name!r} requires omitted path {destination.as_posix()!r}",
                    )
                )

    workflow_ids: set[str] = set()
    for entry in profile.get("workflows", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("source"), str):
            continue
        workflow_path = root / entry["source"]
        workflow_id, roles = _validate_workflow_file(
            root, workflow_path, selected_names, issues
        )
        if workflow_id is not None:
            if workflow_id in workflow_ids:
                issues.append(Issue(display, f"duplicate profile workflow id {workflow_id!r}"))
            workflow_ids.add(workflow_id)
            target = entry.get("target")
            if isinstance(target, str) and Path(target).stem != workflow_id:
                issues.append(
                    Issue(
                        display,
                        f"workflow id {workflow_id!r} does not match target {target!r}",
                    )
                )
        for role in roles:
            if role not in selected_names:
                issues.append(
                    Issue(display, f"profile workflow uses omitted role {role!r}")
                )

    required_workflow_ids = set(REQUIRED_WORKFLOW_IDS)
    if workflow_ids != required_workflow_ids:
        issues.append(
            Issue(
                display,
                "profile workflow ids mismatch; "
                f"missing={sorted(required_workflow_ids - workflow_ids)}, "
                f"unexpected={sorted(workflow_ids - required_workflow_ids)}",
            )
        )

    if config is not None:
        config_target = Path(".codex/config.toml")
        for reference in _config_references(config):
            destination = _relative_config_target(config_target, reference)
            if destination is None or destination not in destinations:
                issues.append(
                    Issue(
                        display,
                        f"base config requires omitted or unsafe path {reference!r}",
                    )
                )


def _validate_profiles(
    root: Path,
    agents: dict[str, tuple[Path, dict[str, Any], tuple[str, ...]]],
    names_by_filename: dict[str, str],
    skills: dict[str, tuple[Path, tuple[tuple[str, bool], ...]]],
    issues: list[Issue],
) -> None:
    try:
        manifest = load_manifest(root)
    except DistributionError as exc:
        issues.append(Issue("distribution/profiles.toml", str(exc)))
        return
    profiles = manifest["profiles"]
    missing_profiles = sorted(set(REQUIRED_PROFILES) - set(profiles))
    extra_profiles = sorted(set(profiles) - set(REQUIRED_PROFILES))
    if missing_profiles:
        issues.append(
            Issue("distribution/profiles.toml", f"missing profiles: {', '.join(missing_profiles)}")
        )
    if extra_profiles:
        issues.append(
            Issue("distribution/profiles.toml", f"unexpected profiles: {', '.join(extra_profiles)}")
        )

    full = profiles.get("full")
    if isinstance(full, dict):
        full_agents = set(full.get("agents", []))
        canonical_agent_files = set(names_by_filename)
        if full_agents != canonical_agent_files:
            missing = sorted(canonical_agent_files - full_agents)
            extra = sorted(full_agents - canonical_agent_files)
            issues.append(
                Issue(
                    "distribution/profiles.toml[full]",
                    f"agent catalog mismatch; missing={missing}, extra={extra}",
                )
            )
        full_skills = set(full.get("skills", []))
        canonical_skills = set(skills)
        if full_skills != canonical_skills:
            missing = sorted(canonical_skills - full_skills)
            extra = sorted(full_skills - canonical_skills)
            issues.append(
                Issue(
                    "distribution/profiles.toml[full]",
                    f"skill catalog mismatch; missing={missing}, extra={extra}",
                )
            )

    config_path = root / manifest.get("base_config", "")
    config = _load_toml(root, config_path, issues) if config_path.is_file() else None
    for profile_name, profile in sorted(profiles.items()):
        if isinstance(profile, dict):
            _validate_profile(
                root,
                profile_name,
                profile,
                config,
                agents,
                names_by_filename,
                skills,
                issues,
            )


def _markdown_section(text: str, heading: str) -> str | None:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return None
    content_start = text.find("\n", start)
    if content_start < 0:
        return ""
    next_heading = text.find("\n## ", content_start + 1)
    return text[content_start + 1 : next_heading if next_heading >= 0 else None]


def _validate_readme_catalogs(
    root: Path,
    agent_names: set[str],
    skill_names: set[str],
    issues: list[Issue],
) -> None:
    path = root / "README.md"
    text = _read_text(root, path, issues)
    if text is None:
        return
    agent_section = _markdown_section(text, "Agent Catalog")
    if agent_section is None:
        issues.append(Issue("README.md", "Agent Catalog section is missing"))
    else:
        documented_agents = set(
            re.findall(r"^\|\s*`([^`]+)`\s*\|", agent_section, re.MULTILINE)
        )
        if documented_agents != agent_names:
            issues.append(
                Issue(
                    "README.md",
                    "agent catalog mismatch; "
                    f"missing={sorted(agent_names - documented_agents)}, "
                    f"unexpected={sorted(documented_agents - agent_names)}",
                )
            )

    skill_section = _markdown_section(text, "Skill Packs")
    if skill_section is None:
        issues.append(Issue("README.md", "Skill Packs section is missing"))
    else:
        documented_skills = set(
            re.findall(r"^-\s+`([^`]+)`(?:\s|$)", skill_section, re.MULTILINE)
        )
        if documented_skills != skill_names:
            issues.append(
                Issue(
                    "README.md",
                    "skill catalog mismatch; "
                    f"missing={sorted(skill_names - documented_skills)}, "
                    f"unexpected={sorted(documented_skills - skill_names)}",
                )
            )


def _validate_review_schema(root: Path, issues: list[Issue]) -> None:
    path = root / REVIEW_SCHEMA_PATH
    display = REVIEW_SCHEMA_PATH.as_posix()
    try:
        with path.open("r", encoding="utf-8") as stream:
            schema = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        issues.append(Issue(display, f"invalid JSON schema: {exc}"))
        return
    if not isinstance(schema, dict):
        issues.append(Issue(display, "schema root must be an object"))
        return
    try:
        validator_namespace = runpy.run_path(
            str(root / REVIEW_SCHEMA_VALIDATOR_PATH)
        )
        runtime_validate_schema = validator_namespace.get("validate_schema")
        if not callable(runtime_validate_schema):
            raise RuntimeError("validate_schema function is missing")
        runtime_validate_schema(schema)
    except Exception as exc:
        issues.append(
            Issue(display, f"runtime schema validator rejected the schema: {exc}")
        )

    expected_required = {"summary", "findings", "residual_risks"}
    required = schema.get("required")
    if not isinstance(required, list) or set(required) != expected_required:
        issues.append(
            Issue(
                display,
                f"top-level required fields must be {sorted(expected_required)}",
            )
        )
    if schema.get("type") != "object":
        issues.append(Issue(display, "top-level type must be 'object'"))
    if schema.get("additionalProperties") is not False:
        issues.append(Issue(display, "top-level additionalProperties must be false"))
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        issues.append(Issue(display, "top-level properties must be an object"))
        return
    if set(properties) != expected_required:
        issues.append(
            Issue(
                display,
                "top-level property catalog must be "
                f"{sorted(expected_required)}",
            )
        )
    expected_types = {
        "summary": "string",
        "findings": "array",
        "residual_risks": "array",
    }
    for name, expected_type in expected_types.items():
        value = properties.get(name)
        if not isinstance(value, dict) or value.get("type") != expected_type:
            issues.append(
                Issue(display, f"properties.{name}.type must be {expected_type!r}")
            )
    findings = properties.get("findings")
    if isinstance(findings, dict):
        items = findings.get("items")
        if not isinstance(items, dict) or items.get("type") != "object":
            issues.append(Issue(display, "properties.findings.items must be an object schema"))
        else:
            expected_finding_required = {
                "id",
                "severity",
                "category",
                "file",
                "title",
                "description",
                "status",
            }
            expected_finding_properties = expected_finding_required | {
                "lines",
                "suggestion",
                "impact",
                "effort",
            }
            item_required = items.get("required")
            if not isinstance(item_required, list) or set(item_required) != expected_finding_required:
                issues.append(
                    Issue(
                        display,
                        "finding required fields must be "
                        f"{sorted(expected_finding_required)}",
                    )
                )
            if items.get("additionalProperties") is not False:
                issues.append(
                    Issue(display, "finding additionalProperties must be false")
                )
            item_properties = items.get("properties")
            if not isinstance(item_properties, dict):
                issues.append(Issue(display, "finding properties must be an object"))
            else:
                if set(item_properties) != expected_finding_properties:
                    issues.append(
                        Issue(
                            display,
                            "finding property catalog must be "
                            f"{sorted(expected_finding_properties)}",
                        )
                    )
                expected_enums = {
                    "severity": {"Critical", "High", "Medium", "Low"},
                    "category": {
                        "security",
                        "bug",
                        "typing",
                        "architecture",
                        "testing",
                        "performance",
                        "compatibility",
                        "convention",
                    },
                    "effort": {"trivial", "small", "medium", "large"},
                    "status": {
                        "pending",
                        "approved",
                        "fixed",
                        "skipped",
                        "wont-fix",
                    },
                }
                for name in expected_finding_properties:
                    field_schema = item_properties.get(name)
                    if not isinstance(field_schema, dict) or field_schema.get("type") != "string":
                        issues.append(
                            Issue(display, f"finding property {name!r} must be a string schema")
                        )
                for name, expected_values in expected_enums.items():
                    field_schema = item_properties.get(name)
                    values = field_schema.get("enum") if isinstance(field_schema, dict) else None
                    if not isinstance(values, list) or set(values) != expected_values:
                        issues.append(
                            Issue(
                                display,
                                f"finding property {name!r} enum must be "
                                f"{sorted(expected_values)}",
                            )
                        )
    residual_risks = properties.get("residual_risks")
    if not isinstance(residual_risks, dict) or residual_risks.get("items") != {"type": "string"}:
        issues.append(
            Issue(display, "properties.residual_risks.items must be a string schema")
        )


def validate_repository(root: Path) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    if yaml is None:
        issues.append(
            Issue(
                "requirements-validation.txt",
                "PyYAML is required; install validation dependencies first",
            )
        )
    _validate_toml_files(root, issues)
    _validate_stack(root, issues)
    _validate_configs(root, issues)
    agents, names_by_filename = _validate_agents(root, issues)
    skills = _validate_skills(root, issues)
    _validate_canonical_workflows(root, set(agents), issues)
    _validate_profiles(root, agents, names_by_filename, skills, issues)
    _validate_readme_catalogs(root, set(agents), set(skills), issues)
    _validate_review_schema(root, issues)
    return sorted(set(issues))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="Repository root to validate (defaults to this checkout).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    issues = validate_repository(args.root)
    if issues:
        for issue in issues:
            print(f"FAIL: {issue.render()}")
        print(f"{len(issues)} integrity error(s) found.")
        return 1
    print("All integrity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
