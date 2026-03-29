from __future__ import annotations

import contextlib
import io
import unittest

from ai_agents.cli import main


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(args)
        return exit_code, stdout.getvalue()

    def test_list_harnesses_shows_opencode_as_default(self) -> None:
        exit_code, output = self.run_cli("list", "harnesses")

        self.assertEqual(exit_code, 0)
        self.assertIn("opencode: default=yes", output)
        self.assertIn("claude: default=no", output)
        self.assertIn("codex: default=no", output)

    def test_build_defaults_to_opencode(self) -> None:
        exit_code, output = self.run_cli("build")

        self.assertEqual(exit_code, 0)
        self.assertIn("Environment: default", output)
        self.assertIn("Harnesses: opencode", output)
        self.assertRegex(output, r"Documents: [1-9]\d*")
        self.assertRegex(output, r"Skills copied: [1-9]\d*")

    def test_build_all_selects_codex(self) -> None:
        exit_code, output = self.run_cli("build", "--all", "--work")

        self.assertEqual(exit_code, 0)
        self.assertIn("Environment: work", output)
        self.assertIn("Harnesses: opencode, claude, codex", output)
        self.assertRegex(output, r"Artifacts: [1-9]\d*")

    def test_lint_passes(self) -> None:
        exit_code, output = self.run_cli("lint")

        self.assertEqual(exit_code, 0)
        self.assertIn("Lint passed", output)
