#!/usr/bin/env python3
"""Validate Codex review JSON against the small schema subset used by this skill."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


TYPE_CHECKS = {
    "array": lambda value: isinstance(value, list),
    "object": lambda value: isinstance(value, dict),
    "string": lambda value: isinstance(value, str),
}


class ValidationError(ValueError):
    """Raised when the schema or review result is outside the supported contract."""


def validate_schema(schema: Any, path: str = "$schema") -> None:
    if not isinstance(schema, dict):
        raise ValidationError(f"{path} must be an object")

    schema_type = schema.get("type")
    if schema_type not in TYPE_CHECKS:
        raise ValidationError(f"{path}.type is missing or unsupported: {schema_type!r}")

    allowed_keys = {"$schema", "title", "description", "type", "enum"}
    if schema_type == "object":
        allowed_keys.update({"properties", "required", "additionalProperties"})
    elif schema_type == "array":
        allowed_keys.add("items")
    unexpected_keys = set(schema) - allowed_keys
    if unexpected_keys:
        names = ", ".join(sorted(unexpected_keys))
        raise ValidationError(f"{path} uses unsupported schema keywords: {names}")

    enum = schema.get("enum")
    if enum is not None and (not isinstance(enum, list) or not enum):
        raise ValidationError(f"{path}.enum must be a non-empty array")
    if enum is not None and not all(TYPE_CHECKS[schema_type](value) for value in enum):
        raise ValidationError(f"{path}.enum values must match type {schema_type}")

    if schema_type == "object":
        properties = schema.get("properties")
        required = schema.get("required", [])
        if not isinstance(properties, dict):
            raise ValidationError(f"{path}.properties must be an object")
        if not isinstance(required, list) or not all(
            isinstance(item, str) for item in required
        ):
            raise ValidationError(f"{path}.required must be an array of strings")
        if len(required) != len(set(required)):
            raise ValidationError(f"{path}.required contains duplicates")
        unknown_required = set(required) - set(properties)
        if unknown_required:
            names = ", ".join(sorted(unknown_required))
            raise ValidationError(f"{path}.required names unknown properties: {names}")
        if schema.get("additionalProperties") is not False:
            raise ValidationError(f"{path}.additionalProperties must be false")
        for name, child in properties.items():
            validate_schema(child, f"{path}.properties.{name}")
    elif schema_type == "array":
        if "items" not in schema:
            raise ValidationError(f"{path}.items is required")
        validate_schema(schema["items"], f"{path}.items")


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> None:
    schema_type = schema["type"]
    if not TYPE_CHECKS[schema_type](instance):
        raise ValidationError(f"{path} must be {schema_type}")

    enum = schema.get("enum")
    if enum is not None and instance not in enum:
        raise ValidationError(f"{path} is not one of the allowed values")

    if schema_type == "object":
        properties = schema["properties"]
        missing = [name for name in schema.get("required", []) if name not in instance]
        if missing:
            raise ValidationError(f"{path} is missing required fields: {', '.join(missing)}")
        unexpected = set(instance) - set(properties)
        if unexpected:
            raise ValidationError(
                f"{path} contains unexpected fields: {', '.join(sorted(unexpected))}"
            )
        for name, value in instance.items():
            validate_instance(value, properties[name], f"{path}.{name}")
    elif schema_type == "array":
        for index, value in enumerate(instance):
            validate_instance(value, schema["items"], f"{path}[{index}]")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-review-output.py SCHEMA", file=sys.stderr)
        return 2

    try:
        schema = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        instance = json.load(sys.stdin)
        validate_schema(schema)
        validate_instance(instance, schema)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"Review output validation failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
