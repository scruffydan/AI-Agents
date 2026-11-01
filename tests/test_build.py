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

    def test_codex_agent_text_survives_toml_rendering(self):
        body = 'Match \\bword\\b in C:\\queries, keep the literal """ delimiter.'
        source = self.root / "source/agents/explore.md"
        _, metadata, _ = source.read_text().split("+++", 2)
        source.write_text(f"+++{metadata}+++\n\n{body}")

        self.build("codex")

        rendered = self.root / "build/codex/.codex/agents/explore.toml"
        instructions = tomllib.loads(rendered.read_text())["developer_instructions"]
        self.assertEqual(instructions.strip(), body)

    def test_codex_explicit_prompt_text_survives_toml_rendering(self):
        body = 'Match \\bword\\b in C:\\queries, keep the literal """ delimiter.'
        (self.root / "source/prompts/brainstorm.md").write_text(body)

        self.build("codex")

        rendered = self.root / "build/codex/.codex/agents/brainstorm.toml"
        instructions = tomllib.loads(rendered.read_text())["developer_instructions"]
        self.assertEqual(instructions.strip(),
                         "Explore ideas without modifying files or running shell commands.\n\n" + body)

    def test_default_build_renders_all_harnesses_with_bare_codex_models(self):
        self.build()

        for harness in ("opencode", "claude", "codex"):
            self.assertTrue((self.root / "build" / harness).is_dir())
        for agent in (self.root / "build/codex/.codex/agents").glob("*.toml"):
            with self.subTest(agent=agent.name):
                self.assertNotIn("/", tomllib.loads(agent.read_text())["model"])

    def test_shared_base_instructions_propagate_to_all_harnesses(self):
        body = (self.root / "source/prompts/AGENTS.md").read_bytes()
        self.build()
        for target in ("opencode/AGENTS.md", "claude/CLAUDE.md", "codex/AGENTS.md"):
            with self.subTest(target=target):
                self.assertEqual((self.root / "build" / target).read_bytes(), body)

    def test_unknown_harness_is_rejected(self):
        result = subprocess.run(
            [sys.executable, "build.py", "cursor"], cwd=self.root, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid harness: cursor", result.stderr)

    def test_brainstorm_follows_work_and_provider_options(self):
        brainstorm = self.root / "build/opencode/agents/brainstorm.md"
        for args, model in (
            ((), "openai/gpt-6-astra#medium"),
            (("--work",), "google-vertex/claude-opus-5-5#high"),
            (("--opencode-provider", "openai"), "openai/gpt-6-astra#medium"),
            (("--work", "--opencode-provider", "openai"), "openai/claude-opus-5-5#high"),
            (("--opencode-provider", "opencode"), "opencode/gpt-6-astra#medium"),
            (("--work", "--opencode-provider", "opencode"), "opencode/claude-opus-5-5#high"),
        ):
            with self.subTest(args=args):
                self.build("opencode", *args)
                self.assertIn(f"model: {model}\n", brainstorm.read_text())
                skill = self.root / "build/opencode/skills/brainstorm-with-agent/SKILL.md"
                self.assertIn(f"select `{model}`", skill.read_text())

    def test_github_copilot_is_rejected_without_replacing_build(self):
        self.build("opencode")
        output = self.root / "build"
        original = {path.relative_to(output): path.read_bytes()
                    for path in output.rglob("*") if path.is_file()}
        for args in ((), ("--work",)):
            with self.subTest(args=args):
                result = subprocess.run(
                    [sys.executable, "build.py", "opencode", *args,
                     "--opencode-provider", "github-copilot"],
                    cwd=self.root, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("invalid choice: 'github-copilot'", result.stderr)
                self.assertEqual(
                    {path.relative_to(output): path.read_bytes()
                     for path in output.rglob("*") if path.is_file()},
                    original,
                )

    def test_shared_skills_and_prompt_modes_exist_for_every_harness(self):
        self.build()
        layouts = {
            "opencode": "skills",
            "claude": "skills",
            "codex": ".agents/skills",
        }
        for harness, directory in layouts.items():
            output = self.root / "build" / harness / directory
            for source in (self.root / "source/skills").glob("*/SKILL.md"):
                with self.subTest(harness=harness, skill=source.parent.name):
                    self.assertEqual(
                        (output / source.relative_to(self.root / "source/skills")).read_bytes(),
                        source.read_bytes(),
                    )
                    for resource in source.parent.glob("*.md"):
                        self.assertEqual(
                            (output / source.parent.name / resource.name).read_bytes(),
                            resource.read_bytes(),
                        )
            for name in ("brainstorm-with-agent", "mode-thorough-plan", "code-review"):
                with self.subTest(harness=harness, skill=name):
                    content = (output / name / "SKILL.md").read_text()
                    self.assertIn(f"name: {name}\n", content)
                    self.assertNotIn("{{prompt:", content)
            for retired in ("mode-brainstorm", "using-code-review", "code-full-review",
                            "command-code-full-review"):
                with self.subTest(harness=harness, retired=retired):
                    self.assertFalse((output / retired).exists())

    def test_brainstorm_models_are_used_by_claude_and_codex(self):
        for args in ((), ("--work",)):
            with self.subTest(args=args):
                self.build(*args)
                claude = self.root / "build/claude/skills/brainstorm-with-agent/SKILL.md"
                self.assertIn("model: claude-opus-5-5\n", claude.read_text())
                self.assertIn("effort: high\n", claude.read_text())
                agent = self.root / "build/codex/.codex/agents/brainstorm.toml"
                parsed = tomllib.loads(agent.read_text())
                self.assertEqual(parsed["model"], "gpt-6-astra")
                self.assertEqual(parsed["model_reasoning_effort"], "medium")
                self.assertFalse(parsed["features"]["shell_tool"])
                skill = self.root / "build/codex/.agents/skills/brainstorm-with-agent/SKILL.md"
                self.assertIn("`brainstorm` custom agent", skill.read_text())

    def test_referenced_shared_skill_support_files_exist(self):
        references = {
            "subagent-driven-development": (
                "implementer-prompt.md", "spec-reviewer-prompt.md", "code-quality-reviewer-prompt.md",
            ),
            "systematic-debugging": (
                "root-cause-tracing.md", "defense-in-depth.md", "condition-based-waiting.md",
            ),
        }
        for skill, filenames in references.items():
            for filename in filenames:
                with self.subTest(skill=skill, resource=filename):
                    path = self.root / "source/skills" / skill / filename
                    self.assertTrue(path.is_file())
                    self.assertTrue(path.read_text().strip())

    def test_opencode_v2_build_has_native_directories_and_no_legacy_agent_fields(self):
        self.build("opencode", "--work")
        output = self.root / "build/opencode"
        for name in ("agents", "skills"):
            self.assertTrue((output / name).is_dir())
        self.assertFalse((output / "commands/code-full-review.md").exists())
        for name in ("agent", "command", "skill"):
            self.assertFalse((output / name).exists())
        for agent in (output / "agents").glob("*.md"):
            with self.subTest(agent=agent.name):
                header = agent.read_text().split("---", 2)[1]
                self.assertNotIn("\npermission:", header)
                self.assertNotIn("\nreasoningEffort:", header)
                self.assertNotIn("\ntemperature:", header)
                self.assertNotIn("google-vertex-anthropic/", header)
        reviewer = (output / "agents/code-security.md").read_text()
        self.assertIn("model: google-vertex/claude-opus-5-5#high\n", reviewer)
        self.assertIn("action: shell\n    resource: \"*\"\n    effect: deny", reviewer)
        commit = (output / "agents/git-commit.md").read_text()
        self.assertIn("model: google-vertex/claude-sonnet-5-5#high\n", commit)
        docs = (output / "agents/docs-fetcher.md").read_text()
        self.assertIn("model: google-vertex/claude-sonnet-5-5#high\n", docs)
        explore = (output / "agents/explore.md").read_text()
        self.assertIn("model: google-vertex/gemini-4-argon#high\n", explore)


if __name__ == "__main__":
    unittest.main()
