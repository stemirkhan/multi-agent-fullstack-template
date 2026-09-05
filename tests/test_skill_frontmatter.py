from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_template import _validate_skills  # noqa: E402


class SkillFrontmatterTests(unittest.TestCase):
    def validate_skill(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / ".agents/skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(text, encoding="utf-8")
            issues = []
            _validate_skills(root, issues)
        return [issue.render() for issue in issues]

    def test_invalid_yaml_is_rejected(self) -> None:
        messages = self.validate_skill(
            '---\nname: example\ndescription: "unterminated\n---\n'
        )
        self.assertTrue(any("invalid frontmatter YAML" in item for item in messages), messages)

    def test_invalid_yaml_timestamp_is_reported_without_crashing(self) -> None:
        messages = self.validate_skill(
            "---\nname: example\ndescription: 2026-99-99\n---\n"
        )
        self.assertTrue(any("invalid frontmatter YAML" in item for item in messages), messages)

    def test_indented_separator_does_not_close_frontmatter(self) -> None:
        messages = self.validate_skill(
            "---\ndescription: |\n  First part\n  ---\n  Second part\n"
            "name: example\n---\n"
        )
        self.assertEqual([], messages)

    def test_invalid_yaml_after_indented_separator_is_still_checked(self) -> None:
        messages = self.validate_skill(
            "---\nname: example\ndescription: |\n  First part\n  ---\n"
            'metadata: "unterminated\n---\n'
        )
        self.assertTrue(any("invalid frontmatter YAML" in item for item in messages), messages)

    def test_duplicate_keys_are_rejected(self) -> None:
        messages = self.validate_skill(
            "---\nname: example\ndescription: first\ndescription: second\n---\n"
        )
        self.assertTrue(any("duplicate key 'description'" in item for item in messages), messages)

    def test_required_fields_must_be_nonempty_strings(self) -> None:
        for field in ("name", "description"):
            for value in ("null", "true", "42", "[]", "{}", "''", "'   '"):
                with self.subTest(field=field, value=value):
                    fields = {"name": "example", "description": "A valid description"}
                    fields[field] = value
                    text = "---\n" + "".join(f"{key}: {item}\n" for key, item in fields.items()) + "---\n"
                    messages = self.validate_skill(text)
                    self.assertTrue(
                        any(f"frontmatter.{field} must be a non-empty string" in item for item in messages),
                        messages,
                    )

    def test_frontmatter_must_be_a_mapping_with_string_keys(self) -> None:
        for content in ("- example\n", "example\n", "1: example\n", ""):
            with self.subTest(content=content):
                messages = self.validate_skill(f"---\n{content}---\n")
                self.assertTrue(any("frontmatter" in item for item in messages), messages)

    def test_missing_delimiters_are_rejected(self) -> None:
        for content in (
            "name: example\ndescription: valid\n",
            "---\nname: example\ndescription: valid\n",
        ):
            with self.subTest(content=content):
                self.assertTrue(self.validate_skill(content))

    def test_valid_yaml_strings_and_metadata_are_accepted(self) -> None:
        for description in (
            '"Read input: preserve # literals"',
            "'Read input: preserve # literals'",
            ">-\n  Read input and\n  preserve boundaries.",
            "|\n  Read input.\n  Preserve boundaries.",
        ):
            with self.subTest(description=description):
                messages = self.validate_skill(
                    f'---\nname: "example" # a YAML comment\ndescription: {description}\n'
                    "metadata:\n  short-description: A short label\n---\n# Example\n"
                )
                self.assertEqual([], messages)


if __name__ == "__main__":
    unittest.main()
