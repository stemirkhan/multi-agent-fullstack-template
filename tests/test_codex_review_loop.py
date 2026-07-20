from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / ".agents/skills/codex-review-loop/scripts/codex-subagent.sh"


class CodexReviewLoopTests(unittest.TestCase):
    def test_uncommitted_review_is_read_only_structured_and_preserves_stdin(self) -> None:
        prompt = "Audit contracts from piped stdin.\nKeep this exact second line.\n"
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            bin_dir = temporary_path / "bin"
            bin_dir.mkdir()
            log_path = temporary_path / "codex-call.json"
            codex_stub = bin_dir / "codex"
            codex_stub.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    import os
                    from pathlib import Path
                    import sys

                    Path(os.environ["CODEX_STUB_LOG"]).write_text(
                        json.dumps({"argv": sys.argv[1:], "stdin": sys.stdin.read()}),
                        encoding="utf-8",
                    )
                    print(json.dumps({
                        "summary": "one issue",
                        "findings": [{
                            "id": "P1",
                            "severity": "Low",
                            "category": "testing",
                            "file": "tests/example.py",
                            "title": "Example finding",
                            "description": "Exercises the item schema.",
                            "status": "pending",
                        }],
                        "residual_risks": [],
                    }))
                    """
                ),
                encoding="utf-8",
            )
            codex_stub.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{bin_dir}{os.pathsep}{environment['PATH']}"
            environment["CODEX_STUB_LOG"] = str(log_path)

            result = subprocess.run(
                ["bash", str(WRAPPER), "--uncommitted"],
                cwd=ROOT,
                env=environment,
                input=prompt,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            invocation = json.loads(log_path.read_text(encoding="utf-8"))

        arguments = invocation["argv"]
        self.assertEqual(["exec", "--sandbox", "read-only", "--ephemeral"], arguments[:4])
        self.assertEqual("review", arguments[4])
        self.assertEqual("--output-schema", arguments[5])
        self.assertTrue(arguments[6].endswith("review-findings.schema.json"))
        self.assertEqual(["--uncommitted", "-"], arguments[7:])
        self.assertNotIn("--full-auto", arguments)
        self.assertEqual(prompt, invocation["stdin"])

    def test_pr_review_pins_exact_head_and_base_oids(self) -> None:
        head_oid = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        base_oid = head_oid
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            bin_dir = temporary_path / "bin"
            bin_dir.mkdir()
            log_path = temporary_path / "codex-call.json"
            codex_stub = bin_dir / "codex"
            codex_stub.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    import os
                    from pathlib import Path
                    import sys

                    Path(os.environ["CODEX_STUB_LOG"]).write_text(
                        json.dumps({"argv": sys.argv[1:], "stdin": sys.stdin.read()}),
                        encoding="utf-8",
                    )
                    print('{"summary": "ok", "findings": [], "residual_risks": []}')
                    """
                ),
                encoding="utf-8",
            )
            codex_stub.chmod(0o755)
            gh_stub = bin_dir / "gh"
            gh_stub.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import os
                    print(os.environ["GH_PR_METADATA"])
                    """
                ),
                encoding="utf-8",
            )
            gh_stub.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{bin_dir}{os.pathsep}{environment['PATH']}"
            environment["CODEX_STUB_LOG"] = str(log_path)
            environment["GH_PR_METADATA"] = (
                f"main\t{base_oid}\tfeature\t{head_oid}"
            )

            result = subprocess.run(
                ["bash", str(WRAPPER), "--pr", "42"],
                cwd=ROOT,
                env=environment,
                input="",
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            invocation = json.loads(log_path.read_text(encoding="utf-8"))

        self.assertEqual(["--base", base_oid, "-"], invocation["argv"][-3:])

    def test_pr_review_rejects_a_stale_local_head(self) -> None:
        base_oid = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            bin_dir = temporary_path / "bin"
            bin_dir.mkdir()
            gh_stub = bin_dir / "gh"
            gh_stub.write_text(
                "#!/usr/bin/env python3\n"
                "import os\n"
                "print(os.environ['GH_PR_METADATA'])\n",
                encoding="utf-8",
            )
            gh_stub.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{bin_dir}{os.pathsep}{environment['PATH']}"
            environment["GH_PR_METADATA"] = (
                f"main\t{base_oid}\tfeature\t{'0' * 40}"
            )

            result = subprocess.run(
                ["bash", str(WRAPPER), "--pr", "42"],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(2, result.returncode)
        self.assertIn("Check out the exact PR head commit", result.stderr)

    def test_pr_review_rejects_an_unavailable_base_object(self) -> None:
        head_oid = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        with tempfile.TemporaryDirectory() as temporary:
            bin_dir = Path(temporary) / "bin"
            bin_dir.mkdir()
            gh_stub = bin_dir / "gh"
            gh_stub.write_text(
                "#!/usr/bin/env python3\n"
                "import os\n"
                "print(os.environ['GH_PR_METADATA'])\n",
                encoding="utf-8",
            )
            gh_stub.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{bin_dir}{os.pathsep}{environment['PATH']}"
            environment["GH_PR_METADATA"] = (
                f"main\t{'0' * 40}\tfeature\t{head_oid}"
            )

            result = subprocess.run(
                ["bash", str(WRAPPER), "--pr", "42"],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(2, result.returncode)
        self.assertIn("is not available locally", result.stderr)

    def test_schema_invalid_codex_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            bin_dir = Path(temporary) / "bin"
            bin_dir.mkdir()
            codex_stub = bin_dir / "codex"
            codex_stub.write_text(
                "#!/usr/bin/env python3\n"
                "print('{\"findings\": []}')\n",
                encoding="utf-8",
            )
            codex_stub.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{bin_dir}{os.pathsep}{environment['PATH']}"

            result = subprocess.run(
                ["bash", str(WRAPPER), "--uncommitted"],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("missing required fields", result.stderr)


if __name__ == "__main__":
    unittest.main()
