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

    def run_install(self, *args, input_text="", force=True):
        env = {**os.environ, "HOME": str(self.home), "PYTHON": sys.executable}
        return subprocess.run(
            ["bash", "install.sh", *args, *(["--force"] if force else [])],
            cwd=self.root, env=env, capture_output=True, text=True, input=input_text,
        )

    def install(self, *args, input_text=""):
        result = self.run_install(*args, input_text=input_text)
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

    def test_all_harnesses_install_shared_skills_and_prompt_modes(self):
        for args in (("--all",), ("--all", "--work")):
            with self.subTest(args=args):
                self.install(*args)
                for directory in (".config/opencode/skills", ".claude/skills", ".agents/skills"):
                    for skill in (self.root / "source/skills").glob("*/SKILL.md"):
                        self.assertTrue((self.home / directory / skill.parent.name / "SKILL.md").is_file())
                    for mode in ("brainstorm-with-agent", "mode-thorough-plan"):
                        self.assertTrue((self.home / directory / mode / "SKILL.md").is_file())
                opencode = self.home / ".config/opencode"
                self.assertTrue((opencode / "agents/brainstorm.md").is_file())
                self.assertFalse((opencode / "commands/code-full-review.md").exists())
                for legacy in ("agent", "command", "skill"):
                    self.assertFalse((opencode / legacy).exists())
                self.assertTrue((self.home / ".codex/agents/brainstorm.toml").is_file())

    def test_opencode_v2_install_preserves_unrelated_entries(self):
        opencode = self.home / ".config/opencode"
        for entry in ("agents/mine.md", "commands/mine.md", "skills/mine/SKILL.md", "agent/legacy.md"):
            path = opencode / entry
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("keep me")
        self.install("opencode")
        for entry in ("agents/mine.md", "commands/mine.md", "skills/mine/SKILL.md", "agent/legacy.md"):
            self.assertEqual((opencode / entry).read_text(), "keep me")

    def test_existing_commands_are_preserved_and_repeat_install_is_unchanged(self):
        command = self.home / ".config/opencode/commands/code-full-review.md"
        command.parent.mkdir(parents=True)
        command.write_text("locally edited review command")

        self.install("opencode")

        self.assertEqual(command.read_text(), "locally edited review command")
        self.assertFalse((self.home / ".ai-agents-backups").exists())
        self.assertTrue((command.parent.parent / "skills/code-review/SKILL.md").is_file())

        result = self.install("opencode")
        self.assertNotIn("Backed up:", result.stdout)
        self.assertNotIn("Installed:", result.stdout)
        self.assertEqual(command.read_text(), "locally edited review command")

    def test_skipped_skill_and_unrelated_command_are_preserved(self):
        self.install("opencode")
        root = self.home / ".config/opencode"
        replacement = root / "skills/code-review/SKILL.md"
        replacement.write_text("keep my review skill")
        command = root / "commands/mine.md"
        command.parent.mkdir(exist_ok=True)
        command.write_text("keep my review command")

        result = self.run_install("opencode", force=False, input_text="n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(replacement.read_text(), "keep my review skill")
        self.assertEqual(command.read_text(), "keep my review command")
        self.assertFalse((self.home / ".ai-agents-backups").exists())

    def test_github_copilot_is_rejected_without_installing(self):
        for args in ((), ("--work",)):
            with self.subTest(args=args):
                result = self.run_install(
                    "opencode", *args, "--opencode-provider", "github-copilot",
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("invalid choice: 'github-copilot'", result.stderr)
                self.assertFalse((self.root / "build").exists())
                self.assertEqual(list(self.home.iterdir()), [])

    def test_shared_base_installs_without_replacing_opencode_settings(self):
        config = self.home / ".config/opencode/opencode.json"
        config.parent.mkdir(parents=True)
        config.write_text('{"providers": {"local": {}}}')

        self.install("codex", "claude", "opencode")

        body = (self.root / "source/prompts/AGENTS.md").read_bytes()
        for target in (".config/opencode/AGENTS.md", ".claude/CLAUDE.md", ".codex/AGENTS.md"):
            with self.subTest(target=target):
                self.assertEqual((self.home / target).read_bytes(), body)
        self.assertEqual(config.read_text(), '{"providers": {"local": {}}}')

    def test_picker_defaults_to_codex_on_enter(self):
        for args in ((), ("--work",)):
            with self.subTest(args=args):
                result = self.install(*args, input_text="\n")
                self.assertIn("1) Codex (default)", result.stdout)
                self.assertLess(result.stdout.index("2) Claude Code"), result.stdout.index("3) OpenCode"))
                self.assertTrue((self.home / ".codex/AGENTS.md").is_file())
                self.assertTrue((self.home / ".codex/agents/explore.toml").is_file())
                self.assertTrue((self.home / ".agents/skills/git-commit/SKILL.md").is_file())
                self.assertFalse((self.home / ".claude").exists())
                self.assertFalse((self.home / ".config/opencode").exists())
                self.assertEqual([p.name for p in (self.root / "build").iterdir()], ["codex"])

    def test_picker_accepts_multiple_numbers_and_names_without_duplicates(self):
        self.install(input_text="claude 3 2 opencode\n")
        self.assertTrue((self.home / ".claude/CLAUDE.md").is_file())
        self.assertTrue((self.home / ".config/opencode/AGENTS.md").is_file())
        self.assertFalse((self.home / ".codex").exists())

    def test_picker_retries_invalid_selection(self):
        result = self.install(input_text="1 invalid\n2\n")
        self.assertIn("Invalid selection: invalid", result.stderr)
        self.assertTrue((self.home / ".claude/CLAUDE.md").is_file())
        self.assertFalse((self.home / ".codex").exists())

    def test_picker_eof_and_conflicting_all_flag_write_nothing(self):
        for args in ((), ("codex", "--all"), ("--all", "opencode")):
            with self.subTest(args=args):
                result = self.run_install(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse((self.root / "build").exists())
                self.assertEqual(list(self.home.iterdir()), [])

    def test_explicit_harnesses_and_all_skip_picker(self):
        for args in (("codex", "claude", "opencode"), ("--all",)):
            with self.subTest(args=args):
                result = self.install(*args)
                self.assertNotIn("Which harnesses", result.stdout)
                targets = (".codex/AGENTS.md", ".claude/CLAUDE.md", ".config/opencode/AGENTS.md")
                self.assertTrue(all((self.home / target).is_file() for target in targets))
                self.assertIn("for codex, claude, opencode", result.stdout)

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
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        backups = list((self.home / ".ai-agents-backups").glob("opencode-*/opencode.json"))
        self.assertEqual([path.read_text() for path in backups], ["old"])
        self.assertEqual(backups[0].stat().st_mode & 0o777, 0o600)
        self.assertEqual(backups[0].parent.stat().st_mode & 0o777, 0o700)

    def test_opencode_init_without_confirmation_preserves_existing_config(self):
        config = self.home / ".config/opencode/opencode.json"
        config.parent.mkdir(parents=True)
        config.write_text("keep me")

        result = self.init_opencode()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(config.read_text(), "keep me")
        self.assertFalse((self.home / ".ai-agents-backups").exists())

    def test_opencode_init_refuses_existing_and_dangling_symlinks(self):
        config = self.home / ".config/opencode/opencode.json"
        config.parent.mkdir(parents=True)
        target = self.home / "other.json"
        for existing in (True, False):
            with self.subTest(existing=existing):
                if existing:
                    target.write_text("keep me")
                config.symlink_to(target)
                result = self.init_opencode("--yes")
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(config.is_symlink())
                if existing:
                    self.assertEqual(target.read_text(), "keep me")
                    target.unlink()
                else:
                    self.assertFalse(target.exists())
                config.unlink()

    def test_opencode_init_fresh_and_unchanged_installs_have_private_permissions(self):
        config = self.home / ".config/opencode/opencode.json"
        result = self.init_opencode()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(config.read_bytes(), (REPO / "source/opencode.json").read_bytes())
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        config.chmod(0o644)

        result = self.init_opencode()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Unchanged:", result.stdout)
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.home / ".ai-agents-backups").exists())


if __name__ == "__main__":
    unittest.main()
