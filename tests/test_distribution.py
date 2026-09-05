from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import distribution_lib  # noqa: E402
import install as install_cli  # noqa: E402
from distribution_lib import (  # noqa: E402
    DistributionError,
    InstallConflict,
    REQUIRED_PROFILES,
    build_profile_plan,
    install_profile,
)
from validate_template import (  # noqa: E402
    extract_read_before,
    missing_workflow_sections,
    parse_workflow,
    validate_repository,
)


class DistributionTests(unittest.TestCase):
    maxDiff = None

    def run_installer(
        self,
        profile: str,
        target: Path,
        *extra: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "install.py"),
                "--profile",
                profile,
                "--target",
                str(target),
                *extra,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def copy_validation_fixture(self, temporary: str) -> Path:
        fixture = Path(temporary) / "fixture"
        fixture.mkdir()
        for relative in (
            ".agents",
            ".codex",
            "distribution",
            "stack",
            "templates",
            "workflows",
        ):
            shutil.copytree(ROOT / relative, fixture / relative)
        for relative in ("AGENTS.md", "README.md"):
            shutil.copy2(ROOT / relative, fixture / relative)
        return fixture

    def test_repository_integrity(self) -> None:
        issues = validate_repository(ROOT)
        self.assertEqual([], [issue.render() for issue in issues])

    def test_missing_read_before_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            agent_path = fixture / ".codex/agents/qa_debugger.toml"
            text = agent_path.read_text(encoding="utf-8")
            text = text.replace(
                "Read before acting:\n",
                "Read before acting:\n- missing/audit-reference.md\n",
                1,
            )
            agent_path.write_text(text, encoding="utf-8")

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any(
                "Read before acting path is missing: missing/audit-reference.md" in message
                for message in messages
            ),
            messages,
        )

    def test_explicit_agent_config_registration_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            config_path = fixture / ".codex/config.toml"
            config_path.write_text(
                config_path.read_text(encoding="utf-8")
                + '\n[agents.qa_debugger]\nconfig_file = "agents/qa_debugger.toml"\n',
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("nested agents.*.config_file is not allowed" in message for message in messages),
            messages,
        )

    def test_multi_agent_feature_cannot_be_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            config_path = fixture / ".codex/config.toml"
            config_path.write_text(
                config_path.read_text(encoding="utf-8").replace(
                    "multi_agent = true", "multi_agent = false", 1
                ),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("features.multi_agent must be true" in message for message in messages),
            messages,
        )

    def test_read_only_agent_cannot_gain_write_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            agent_path = fixture / ".codex/agents/reviewer_guard.toml"
            agent_path.write_text(
                agent_path.read_text(encoding="utf-8").replace(
                    'sandbox_mode = "read-only"',
                    'sandbox_mode = "danger-full-access"',
                    1,
                ),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("sandbox_mode must be 'read-only'" in message for message in messages),
            messages,
        )

    def test_missing_workflow_error_handling_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            workflow_path = fixture / "distribution/workflows/backend/bugfix.yaml"
            text = workflow_path.read_text(encoding="utf-8")
            workflow_path.write_text(
                text.split("error_handling:", 1)[0],
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("workflow section is missing: error_handling" in message for message in messages),
            messages,
        )

    def test_noncanonical_role_alias_in_workflow_prose_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            workflow_path = fixture / "workflows/bugfix.yaml"
            text = workflow_path.read_text(encoding="utf-8")
            workflow_path.write_text(
                text.replace("qa_debugger documents", "qa-debugger documents", 1),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("non-canonical role alias 'qa-debugger'" in message for message in messages),
            messages,
        )

    def test_duplicate_yaml_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            workflow_path = fixture / "workflows/bugfix.yaml"
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8") + "\nid: duplicate\n",
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any(
                "invalid YAML" in message and "duplicate key 'id'" in message
                for message in messages
            ),
            messages,
        )

    def test_invalid_workflow_shape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            workflow_path = fixture / "distribution/workflows/frontend/refactor.yaml"
            text = workflow_path.read_text(encoding="utf-8")
            before_sequence, after_sequence = text.split("sequence:\n", 1)
            _, after_done_when = after_sequence.split("done_when:\n", 1)
            workflow_path.write_text(
                before_sequence
                + "sequence: reviewer_guard\n"
                + "done_when:\n"
                + after_done_when,
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("workflow.sequence must be a non-empty list" in message for message in messages),
            messages,
        )

    def test_workflow_fields_are_type_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            workflow_path = fixture / "distribution/workflows/backend/bugfix.yaml"
            workflow_path.write_text(
                """id: bugfix
goal: []
sequence:
  - role: tech_lead_orchestrator
    output: []
done_when: complete
error_handling: []
""",
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        expected = (
            "workflow.goal must be a non-empty string",
            "workflow.sequence[0].output must be a non-empty string",
            "workflow.done_when must be a non-empty list of strings",
            "workflow.error_handling must be a non-empty mapping",
        )
        for fragment in expected:
            with self.subTest(fragment=fragment):
                self.assertTrue(
                    any(fragment in message for message in messages),
                    messages,
                )

    def test_invalid_stack_shape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            stack_path = fixture / "stack/default-stack.yaml"
            text = stack_path.read_text(encoding="utf-8")
            before_runtime, after_runtime = text.split("  runtime:\n", 1)
            _, after_framework = after_runtime.split("  framework:", 1)
            stack_path.write_text(
                before_runtime
                + "  runtime: python-3.12\n"
                + "  framework:"
                + after_framework,
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("stack.backend.runtime must be a mapping" in message for message in messages),
            messages,
        )

    def test_required_profile_table_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            manifest_path = fixture / "distribution/profiles.toml"
            text = manifest_path.read_text(encoding="utf-8")
            manifest_path.write_text(
                text.replace("[profiles.frontend]", "[profiles.web]", 1),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any(
                "profile tables mismatch" in message and "frontend" in message
                for message in messages
            ),
            messages,
        )

    def test_profile_requires_exact_workflow_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            workflow_path = fixture / "distribution/workflows/frontend/refactor.yaml"
            text = workflow_path.read_text(encoding="utf-8")
            workflow_path.write_text(
                text.replace("id: refactor", "id: frontend-cleanup", 1),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("profile workflow ids mismatch" in message for message in messages),
            messages,
        )

    def test_full_profile_must_use_canonical_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            manifest_path = fixture / "distribution/profiles.toml"
            text = manifest_path.read_text(encoding="utf-8")
            manifest_path.write_text(
                text.replace(
                    'source = "workflows/bugfix.yaml"',
                    'source = "distribution/workflows/backend/bugfix.yaml"',
                    1,
                ),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("must copy the canonical workflow files" in message for message in messages),
            messages,
        )

    def test_profiles_must_use_canonical_stack_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            manifest_path = fixture / "distribution/profiles.toml"
            text = manifest_path.read_text(encoding="utf-8")
            manifest_path.write_text(
                text.replace(
                    'source = "stack/default-stack.yaml"',
                    'source = "templates/project-AGENTS.backend.md"',
                    1,
                ),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any(
                "must copy the canonical stack/default-stack.yaml" in message
                for message in messages
            ),
            messages,
        )

    def test_profile_must_use_its_matching_project_template(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            manifest_path = fixture / "distribution/profiles.toml"
            manifest_path.write_text(
                manifest_path.read_text(encoding="utf-8").replace(
                    'agents_template = "templates/project-AGENTS.backend.md"',
                    'agents_template = "templates/project-AGENTS.md"',
                    1,
                ),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("must use templates/project-AGENTS.backend.md" in message for message in messages),
            messages,
        )

    def test_readme_agent_catalog_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            readme_path = fixture / "README.md"
            text = readme_path.read_text(encoding="utf-8")
            readme_path.write_text(
                text.replace("| `reviewer_guard` |", "| `reviewer_guard_old` |", 1),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("agent catalog mismatch" in message for message in messages),
            messages,
        )

    def test_review_schema_top_level_contract_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            schema_path = (
                fixture
                / ".agents/skills/codex-review-loop/references/schemas/review-findings.schema.json"
            )
            text = schema_path.read_text(encoding="utf-8")
            schema_path.write_text(
                text.replace(
                    '"required": ["summary", "findings", "residual_risks"]',
                    '"required": ["summary", "findings"]',
                    1,
                ),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("top-level required fields" in message for message in messages),
            messages,
        )

    def test_review_schema_finding_contract_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            schema_path = (
                fixture
                / ".agents/skills/codex-review-loop/references/schemas/review-findings.schema.json"
            )
            text = schema_path.read_text(encoding="utf-8")
            schema_path.write_text(
                text.replace(
                    '          "status"\n        ],',
                    '          "impact"\n        ],',
                    1,
                ),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("finding required fields" in message for message in messages),
            messages,
        )

    def test_review_schema_runtime_subset_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.copy_validation_fixture(temporary)
            schema_path = (
                fixture
                / ".agents/skills/codex-review-loop/references/schemas/review-findings.schema.json"
            )
            schema_path.write_text(
                schema_path.read_text(encoding="utf-8").replace(
                    '"summary": {\n      "type": "string"\n    }',
                    '"summary": {\n      "type": "string",\n      "minLength": 1\n    }',
                    1,
                ),
                encoding="utf-8",
            )

            issues = validate_repository(fixture)

        messages = [issue.render() for issue in issues]
        self.assertTrue(
            any("runtime schema validator rejected" in message for message in messages),
            messages,
        )

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            result = self.run_installer("backend", target, "--dry-run")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("DRY-RUN profile=backend", result.stdout)
            self.assertFalse(target.exists())

    def test_existing_file_blocks_install_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            agents_file = target / "AGENTS.md"
            agents_file.write_text("keep me\n", encoding="utf-8")

            result = self.run_installer("frontend", target)

            self.assertEqual(2, result.returncode)
            self.assertIn("CONFLICT AGENTS.md", result.stderr)
            self.assertEqual("keep me\n", agents_file.read_text(encoding="utf-8"))
            self.assertFalse((target / ".codex").exists())

    def test_conflicting_dry_run_prints_plan_and_conflicts_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project with conflicts"
            target.mkdir()
            agents_file = target / "AGENTS.md"
            agents_file.write_text("keep me\n", encoding="utf-8")

            result = self.run_installer("frontend", target, "--dry-run")

            self.assertEqual(2, result.returncode)
            self.assertIn("DRY-RUN profile=frontend", result.stdout)
            self.assertIn("COPY .codex/config.toml -> .codex/config.toml", result.stdout)
            self.assertIn("would_overwrite=1", result.stdout)
            self.assertIn("CONFLICT AGENTS.md", result.stderr)
            self.assertEqual("keep me\n", agents_file.read_text(encoding="utf-8"))
            self.assertFalse((target / ".codex").exists())

    def test_force_replaces_reviewed_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            agents_file = target / "AGENTS.md"
            agents_file.write_text("replace me\n", encoding="utf-8")

            result = self.run_installer("backend", target, "--force")

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("overwritten=1", result.stdout)
            self.assertEqual(
                (ROOT / "templates/project-AGENTS.backend.md").read_text(encoding="utf-8"),
                agents_file.read_text(encoding="utf-8"),
            )

    def test_no_force_toctou_conflict_rolls_back_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            original_preflight = distribution_lib.preflight_install

            def racing_preflight(*args: object, **kwargs: object):
                normalized, conflicts = original_preflight(*args, **kwargs)
                normalized.mkdir()
                (normalized / "AGENTS.md").write_text("racer\n", encoding="utf-8")
                return normalized, conflicts

            with mock.patch.object(
                distribution_lib,
                "preflight_install",
                side_effect=racing_preflight,
            ):
                with self.assertRaises(InstallConflict):
                    install_profile(ROOT, "frontend", target)

            self.assertEqual("racer\n", (target / "AGENTS.md").read_text(encoding="utf-8"))
            actual = {
                path.relative_to(target).as_posix()
                for path in target.rglob("*")
                if path.is_file() or path.is_symlink()
            }
            self.assertEqual({"AGENTS.md"}, actual)

    def test_parent_symlink_race_cannot_escape_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            target = base / "project"
            outside = base / "outside"
            target.mkdir()
            outside.mkdir()
            original_preflight = distribution_lib.preflight_install

            def racing_preflight(*args: object, **kwargs: object):
                result = original_preflight(*args, **kwargs)
                (target / ".codex").symlink_to(outside, target_is_directory=True)
                return result

            with mock.patch.object(
                distribution_lib,
                "preflight_install",
                side_effect=racing_preflight,
            ):
                with self.assertRaises(DistributionError):
                    install_profile(ROOT, "frontend", target)

            self.assertEqual([], list(outside.iterdir()))
            self.assertTrue((target / ".codex").is_symlink())
            self.assertFalse((target / ".agents").exists())

    def test_target_root_swap_is_detected_and_rolled_back(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            target = base / "project"
            displaced = base / "displaced"
            target.mkdir()
            original_commit = distribution_lib._commit_staged_file
            calls = 0

            def moving_commit(*args: object, **kwargs: object):
                nonlocal calls
                result = original_commit(*args, **kwargs)
                calls += 1
                if calls == 1:
                    target.rename(displaced)
                    target.mkdir()
                return result

            with mock.patch.object(
                distribution_lib,
                "_commit_staged_file",
                side_effect=moving_commit,
            ):
                with self.assertRaises(DistributionError):
                    install_profile(ROOT, "frontend", target)

            self.assertEqual([], list(target.iterdir()))
            self.assertEqual([], list(displaced.iterdir()))

    def test_keyboard_interrupt_rolls_back_new_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            original_copy = distribution_lib._copy_to_secure_temp
            calls = 0

            def interrupted_copy(*args: object, **kwargs: object):
                nonlocal calls
                calls += 1
                if calls == 4:
                    raise KeyboardInterrupt
                return original_copy(*args, **kwargs)

            with mock.patch.object(
                distribution_lib,
                "_copy_to_secure_temp",
                side_effect=interrupted_copy,
            ):
                with self.assertRaises(KeyboardInterrupt):
                    install_profile(ROOT, "frontend", target)

            self.assertFalse(target.exists())

    def test_transient_temp_unlink_failure_rolls_back_current_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            original_unlink = distribution_lib.os.unlink
            failed = False

            def flaky_unlink(path: object, *args: object, **kwargs: object):
                nonlocal failed
                if not failed and ".template-new-" in str(path):
                    failed = True
                    raise OSError("injected transient unlink failure")
                return original_unlink(path, *args, **kwargs)

            with mock.patch.object(
                distribution_lib,
                "_require_secure_install_primitives",
            ), mock.patch.object(
                distribution_lib.os,
                "unlink",
                side_effect=flaky_unlink,
            ):
                with self.assertRaises(DistributionError):
                    install_profile(ROOT, "frontend", target)

            self.assertTrue(failed)
            self.assertFalse(target.exists())

    def test_cli_reports_committed_interrupt_during_backup_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            operations = build_profile_plan(ROOT, "frontend")
            originals = operations[:2]
            for operation in originals:
                destination = target / operation.destination
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text("original\n", encoding="utf-8")
            original_unlink = distribution_lib.os.unlink
            backup_unlinks = 0

            def interrupted_unlink(path: object, *args: object, **kwargs: object):
                nonlocal backup_unlinks
                if ".template-backup-" in str(path):
                    backup_unlinks += 1
                    if backup_unlinks == 2:
                        raise KeyboardInterrupt
                return original_unlink(path, *args, **kwargs)

            stderr = StringIO()
            with mock.patch.object(
                distribution_lib,
                "_require_secure_install_primitives",
            ), mock.patch.object(
                distribution_lib.os,
                "unlink",
                side_effect=interrupted_unlink,
            ), redirect_stderr(stderr):
                return_code = install_cli.main(
                    ["--profile", "frontend", "--target", str(target), "--force"]
                )

            self.assertEqual(130, return_code)
            self.assertEqual(2, backup_unlinks)
            self.assertIn("Install committed", stderr.getvalue())
            self.assertIn("cleanup was interrupted", stderr.getvalue())
            self.assertIn("Installed files remain", stderr.getvalue())
            self.assertNotIn("rolled back", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())
            for operation in operations:
                self.assertEqual(
                    operation.source.read_bytes(),
                    (target / operation.destination).read_bytes(),
                )
            backups = list(target.rglob("*.template-backup-*"))
            self.assertEqual(1, len(backups))
            self.assertEqual("original\n", backups[0].read_text(encoding="utf-8"))

    def test_cli_rolls_back_force_install_when_interrupted_before_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            first_destination = build_profile_plan(ROOT, "frontend")[0].destination
            existing = target / first_destination
            existing.parent.mkdir(parents=True)
            existing.write_text("original\n", encoding="utf-8")
            original_copy = distribution_lib._copy_to_secure_temp
            calls = 0

            def interrupted_copy(*args: object, **kwargs: object):
                nonlocal calls
                calls += 1
                if calls == 4:
                    raise KeyboardInterrupt
                return original_copy(*args, **kwargs)

            stderr = StringIO()
            with mock.patch.object(
                distribution_lib,
                "_copy_to_secure_temp",
                side_effect=interrupted_copy,
            ), redirect_stderr(stderr):
                return_code = install_cli.main(
                    ["--profile", "frontend", "--target", str(target), "--force"]
                )

            self.assertEqual(130, return_code)
            self.assertIn("applied changes were rolled back", stderr.getvalue())
            self.assertNotIn("Install committed", stderr.getvalue())
            self.assertEqual("original\n", existing.read_text(encoding="utf-8"))
            actual = {
                path.relative_to(target).as_posix()
                for path in target.rglob("*")
                if path.is_file() or path.is_symlink()
            }
            self.assertEqual({first_destination.as_posix()}, actual)

    def test_cli_reports_committed_interrupt_during_descriptor_cleanup(self) -> None:
        for interrupted_descriptor in ("operation", "root", "target_parent"):
            with (
                self.subTest(descriptor=interrupted_descriptor),
                tempfile.TemporaryDirectory() as temporary,
            ):
                target = Path(temporary) / "project"
                operations = build_profile_plan(ROOT, "frontend")
                original_commit = distribution_lib._commit_staged_file
                original_verify = distribution_lib._verify_install_root
                original_close = distribution_lib.os.close
                descriptors: dict[str, int] = {}
                operation_descriptors: set[int] = set()
                closed: set[int] = set()
                interrupted = False

                def recording_commit(parent_fd: int, *args: object, **kwargs: object):
                    result = original_commit(parent_fd, *args, **kwargs)
                    operation_descriptors.add(parent_fd)
                    descriptors.setdefault("operation", parent_fd)
                    return result

                def recording_verify(
                    path: Path,
                    target_parent_fd: int,
                    root_fd: int,
                    identity: tuple[int, int],
                ) -> None:
                    descriptors.update(target_parent=target_parent_fd, root=root_fd)
                    original_verify(path, target_parent_fd, root_fd, identity)

                def interrupted_close(descriptor: int) -> None:
                    nonlocal interrupted
                    original_close(descriptor)
                    if len(operation_descriptors) == len(operations) and (
                        descriptor in operation_descriptors
                        or descriptor in descriptors.values()
                    ):
                        closed.add(descriptor)
                        if (
                            not interrupted
                            and descriptor == descriptors[interrupted_descriptor]
                        ):
                            interrupted = True
                            raise KeyboardInterrupt

                stderr = StringIO()
                with mock.patch.object(
                    distribution_lib, "_commit_staged_file", side_effect=recording_commit
                ), mock.patch.object(
                    distribution_lib, "_verify_install_root", side_effect=recording_verify
                ), mock.patch.object(
                    distribution_lib.os, "close", side_effect=interrupted_close
                ), redirect_stderr(stderr):
                    return_code = install_cli.main(
                        ["--profile", "frontend", "--target", str(target)]
                    )

                # Also release remaining descriptors when exercising the unfixed path.
                expected_descriptors = operation_descriptors | set(descriptors.values())
                for descriptor in expected_descriptors - closed:
                    original_close(descriptor)
                self.assertTrue(interrupted)
                self.assertEqual(130, return_code)
                self.assertIn("Install committed", stderr.getvalue())
                self.assertNotIn("rolled back", stderr.getvalue())
                self.assertEqual(expected_descriptors, closed)
                for operation in operations:
                    self.assertEqual(
                        operation.source.read_bytes(),
                        (target / operation.destination).read_bytes(),
                    )

    def test_force_install_rolls_back_on_late_oserror(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            first_destination = build_profile_plan(ROOT, "backend")[0].destination
            existing = target / first_destination
            existing.parent.mkdir(parents=True)
            existing.write_text("original\n", encoding="utf-8")
            original_copy = distribution_lib._copy_to_secure_temp
            calls = 0

            def failing_copy(*args: object, **kwargs: object):
                nonlocal calls
                calls += 1
                if calls == 5:
                    raise OSError("injected disk failure")
                return original_copy(*args, **kwargs)

            with mock.patch.object(
                distribution_lib,
                "_copy_to_secure_temp",
                side_effect=failing_copy,
            ):
                with self.assertRaises(DistributionError) as raised:
                    install_profile(ROOT, "backend", target, force=True)

            self.assertIn("injected disk failure", str(raised.exception))
            self.assertEqual("original\n", existing.read_text(encoding="utf-8"))
            actual = {
                path.relative_to(target).as_posix()
                for path in target.rglob("*")
                if path.is_file() or path.is_symlink()
            }
            self.assertEqual({first_destination.as_posix()}, actual)

    def test_late_non_os_exception_restores_current_force_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            first_destination = build_profile_plan(ROOT, "backend")[0].destination
            existing = target / first_destination
            existing.parent.mkdir(parents=True)
            existing.write_text("original\n", encoding="utf-8")

            with mock.patch.object(
                distribution_lib,
                "_installed_identity",
                side_effect=RuntimeError("injected late failure"),
            ):
                with self.assertRaises(DistributionError) as raised:
                    install_profile(ROOT, "backend", target, force=True)

            self.assertIn("injected late failure", str(raised.exception))
            self.assertEqual("original\n", existing.read_text(encoding="utf-8"))
            actual = {
                path.relative_to(target).as_posix()
                for path in target.rglob("*")
                if path.is_file() or path.is_symlink()
            }
            self.assertEqual({first_destination.as_posix()}, actual)

    def test_generic_failure_removes_new_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            original_copy = distribution_lib._copy_to_secure_temp
            calls = 0

            def failing_copy(*args: object, **kwargs: object):
                nonlocal calls
                calls += 1
                if calls == 4:
                    raise RuntimeError("injected generic failure")
                return original_copy(*args, **kwargs)

            with mock.patch.object(
                distribution_lib,
                "_copy_to_secure_temp",
                side_effect=failing_copy,
            ):
                with self.assertRaises(DistributionError) as raised:
                    install_profile(ROOT, "frontend", target)

            self.assertIn("injected generic failure", str(raised.exception))
            self.assertFalse(target.exists())

    def test_cli_handles_raw_oserror_without_traceback(self) -> None:
        stderr = StringIO()
        with mock.patch.object(
            install_cli,
            "install_profile",
            side_effect=OSError("injected permission failure"),
        ), redirect_stderr(stderr):
            return_code = install_cli.main(
                ["--profile", "backend", "--target", "/unused"]
            )

        self.assertEqual(2, return_code)
        self.assertIn("operating-system error", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_profile_install_smoke_and_exact_file_set(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for profile in REQUIRED_PROFILES:
                with self.subTest(profile=profile):
                    target = base / f"{profile} project"
                    result = self.run_installer(profile, target)
                    self.assertEqual(0, result.returncode, result.stderr)

                    expected = {
                        operation.destination.as_posix()
                        for operation in build_profile_plan(ROOT, profile)
                    }
                    actual = {
                        path.relative_to(target).as_posix()
                        for path in target.rglob("*")
                        if path.is_file()
                    }
                    self.assertEqual(expected, actual)
                    self._assert_installed_agent_references(target)
                    self._assert_installed_workflow_roles(target)

            self.assertFalse(
                (base / "backend project/.codex/agents/frontend_implementer.toml").exists()
            )
            self.assertFalse(
                (base / "frontend project/.codex/agents/backend_implementer.toml").exists()
            )
            self.assertTrue(
                (base / "full project/.codex/agents/integration_contract_keeper.toml").is_file()
            )

    def _assert_installed_agent_references(self, target: Path) -> None:
        for agent_path in sorted((target / ".codex/agents").glob("*.toml")):
            with agent_path.open("rb") as stream:
                agent = tomllib.load(stream)
            for reference in extract_read_before(agent["developer_instructions"]):
                self.assertTrue(
                    (target / reference).is_file(),
                    f"{agent_path.name} requires missing {reference}",
                )

    def _assert_installed_workflow_roles(self, target: Path) -> None:
        agent_names: set[str] = set()
        for agent_path in (target / ".codex/agents").glob("*.toml"):
            with agent_path.open("rb") as stream:
                agent_names.add(tomllib.load(stream)["name"])
        for workflow_path in sorted((target / "workflows").glob("*.yaml")):
            text = workflow_path.read_text(encoding="utf-8")
            _, roles = parse_workflow(text)
            self.assertTrue(roles, f"{workflow_path} contains no roles")
            self.assertEqual((), missing_workflow_sections(text), workflow_path)
            self.assertTrue(
                set(roles) <= agent_names,
                f"{workflow_path} references an omitted agent",
            )


if __name__ == "__main__":
    unittest.main()
