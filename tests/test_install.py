"""Installer checks; every write stays in a temporary repository copy and HOME."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repo"
        self.home = Path(temporary.name) / "home"
        self.home.mkdir()
        for name in ("source", "templates"):
            shutil.copytree(REPO / name, self.root / name)
        for name in ("build.py", "install.sh"):
            shutil.copy2(REPO / name, self.root / name)

    def install(self, *args):
        env = {**os.environ, "HOME": str(self.home), "PYTHON": sys.executable}
        result = subprocess.run(
            ["bash", "install.sh", *args, "--force"],
            cwd=self.root, env=env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_unrelated_skills_and_agents_are_preserved(self):
        unrelated_skill = self.home / ".claude/skills/my-own-skill/SKILL.md"
        unrelated_agent = self.home / ".codex/agents/my-own-agent.toml"
        for path in (unrelated_skill, unrelated_agent):
            path.parent.mkdir(parents=True)
            path.write_text("keep me")

        self.install("claude", "codex")

        self.assertEqual(unrelated_skill.read_text(), "keep me")
        self.assertEqual(unrelated_agent.read_text(), "keep me")
        self.assertTrue((self.home / ".claude/skills/git-commit/SKILL.md").is_file())
        self.assertTrue((self.home / ".codex/agents/explore.toml").is_file())

    def test_changed_files_are_backed_up_and_unchanged_files_are_skipped(self):
        self.install("claude")
        agent = self.home / ".claude/agents/explore.md"
        generated = agent.read_text()
        agent.write_text("local edit")

        result = self.install("claude")

        self.assertEqual(agent.read_text(), generated)
        backups = list((self.home / ".ai-agents-backups").glob("*/.claude/agents/explore.md"))
        self.assertEqual([path.read_text() for path in backups], ["local edit"])
        self.assertEqual(result.stdout.count("Backed up:"), 1)
        self.assertEqual(result.stdout.count("Installed:"), 1)

    def init_opencode(self, *args):
        shutil.copy2(REPO / "opencode-init.sh", self.root / "opencode-init.sh")
        return subprocess.run(
            ["bash", "opencode-init.sh", *args],
            cwd=self.root, env={**os.environ, "HOME": str(self.home)},
            capture_output=True, text=True, stdin=subprocess.DEVNULL,
        )

    def test_opencode_init_help_and_unknown_options_write_nothing(self):
        config = self.home / ".config/opencode/opencode.json"
        for args, code in ((("--help",), 0), (("-h",), 0), (("--bogus",), 1)):
            with self.subTest(args=args):
                result = self.init_opencode(*args)
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                self.assertIn("Usage:", result.stdout + result.stderr)
                self.assertFalse(config.exists())

    def test_opencode_init_yes_overwrites_existing_config(self):
        config = self.home / ".config/opencode/opencode.json"
        config.parent.mkdir(parents=True)
        config.write_text("old")

        result = self.init_opencode("--yes")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(config.read_text(), (REPO / "source/opencode.json").read_text())


if __name__ == "__main__":
    unittest.main()
