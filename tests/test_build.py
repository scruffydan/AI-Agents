"""Build checks; every write stays in a temporary repository copy."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest


REPO = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("source", "templates"):
            shutil.copytree(REPO / name, self.root / name)
        shutil.copy2(REPO / "build.py", self.root / "build.py")

    def build(self, *args):
        result = subprocess.run(
            [sys.executable, "build.py", *args], cwd=self.root, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_codex_prompt_text_survives_toml_rendering(self):
        body = 'Match \\bword\\b in C:\\queries, keep the literal """ delimiter.'
        (self.root / "source/prompts/explore.md").write_text(body)

        self.build("codex")

        rendered = self.root / "build/codex/.codex/agents/explore.toml"
        instructions = tomllib.loads(rendered.read_text())["developer_instructions"]
        self.assertEqual(instructions.strip(), body)

    def test_default_build_renders_all_harnesses_with_bare_codex_models(self):
        self.build()

        for harness in ("opencode", "claude", "codex"):
            self.assertTrue((self.root / "build" / harness).is_dir())
        for agent in (self.root / "build/codex/.codex/agents").glob("*.toml"):
            with self.subTest(agent=agent.name):
                self.assertNotIn("/", tomllib.loads(agent.read_text())["model"])

    def test_unknown_harness_is_rejected(self):
        result = subprocess.run(
            [sys.executable, "build.py", "cursor"], cwd=self.root, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid harness: cursor", result.stderr)

    def test_brainstorm_follows_work_and_provider_options(self):
        brainstorm = self.root / "build/opencode/agent/brainstorm.md"
        for args, model in (
            ((), "openai/gpt-6-astra"),
            (("--work",), "google-vertex-anthropic/claude-opus-5-5"),
            (("--opencode-provider", "github-copilot"), "github-copilot/gpt-6-astra"),
        ):
            with self.subTest(args=args):
                self.build("opencode", *args)
                self.assertIn(f"model: {model}\n", brainstorm.read_text())


if __name__ == "__main__":
    unittest.main()
