"""Installer checks; every write stays in a temporary repository copy and HOME."""

import json
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
        shutil.copytree(REPO / "source", self.root / "source")
        for name in ("build.py", "renderers.py", "install.py", "THIRD_PARTY_NOTICES.md"):
            shutil.copy2(REPO / name, self.root / name)

    def run_install(self, *args, input_text="", force=True):
        env = {**os.environ, "HOME": str(self.home)}
        return subprocess.run(
            [sys.executable, "install.py", *args, *(["--force"] if force else [])],
            cwd=self.root, env=env, capture_output=True, text=True, input=input_text,
        )

    def install(self, *args, input_text=""):
        result = self.run_install(*args, input_text=input_text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_notices_install_beside_base_instructions_for_all_harnesses(self):
        self.install("--all")
        notices = (self.root / "THIRD_PARTY_NOTICES.md").read_bytes()
        for directory in (".codex", ".claude", ".config/opencode", ".gemini/config"):
            with self.subTest(directory=directory):
                self.assertEqual(
                    (self.home / directory / "THIRD_PARTY_NOTICES.md").read_bytes(),
                    notices,
                )

        result = self.install("--all")
        self.assertNotIn("Installed:", result.stdout)
        self.assertFalse((self.home / ".ai-agents-backups").exists())

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
        self.assertTrue((self.home / ".codex/agents/code-security.toml").is_file())

    def test_antigravity_installs_under_its_config_dir_without_touching_gemini_cli(self):
        gemini_cli = self.home / ".gemini/GEMINI.md"
        gemini_cli.parent.mkdir()
        gemini_cli.write_text("Gemini CLI context")

        self.install("antigravity")

        config = self.home / ".gemini/config"
        self.assertEqual(gemini_cli.read_text(), "Gemini CLI context")
        self.assertEqual(
            (config / "AGENTS.md").read_bytes(),
            (self.root / "source/prompts/AGENTS.md").read_bytes(),
        )
        self.assertTrue((config / "skills/git-commit/SKILL.md").is_file())
        self.assertTrue((config / "agents/code-security.md").is_file())

    def test_retired_agents_move_to_backup_unless_still_built_or_declined(self):
        agents = self.root / "source/agents"
        (agents / "code-simplifier.md").unlink(missing_ok=True)
        shutil.copy2(agents / "docs-fetcher.md", agents / "code-redundancy.md")
        leftovers = [
            self.home / directory / f"code-simplifier{suffix}"
            for directory, suffix in (
                (".claude/agents", ".md"), (".codex/agents", ".toml"),
                (".config/opencode/agents", ".md"),
            )
        ]
        for leftover in leftovers:
            leftover.parent.mkdir(parents=True)
            leftover.write_text("retired copy")

        result = self.run_install("--all", force=False, input_text="n\nn\nn\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([path.read_text() for path in leftovers], ["retired copy"] * 3)
        self.assertFalse((self.home / ".ai-agents-backups").exists())

        self.install("--all")

        self.assertFalse(any(path.exists() for path in leftovers))
        backups = sorted(
            path.relative_to(self.home / ".ai-agents-backups").parts[1:]
            for path in (self.home / ".ai-agents-backups").rglob("*") if path.is_file()
        )
        self.assertEqual(
            backups, sorted(path.relative_to(self.home).parts for path in leftovers),
        )
        self.assertTrue((self.home / ".claude/agents/code-redundancy.md").is_file())

    def test_installer_excludes_os_metadata_added_to_build(self):
        script = """
from pathlib import Path
import build
import install

build.build(list(build.HARNESSES))
for harness in build.HARNESSES:
    output = build.BUILD / harness
    skills = output / build.LAYOUT[harness]["skills"]
    agents = output / Path(build.AGENT_PATHS[harness]).parent
    for directory in (agents, skills, skills / "code-review"):
        for name in (".DS_Store", "Thumbs.db", "ehthumbs.db", "Desktop.ini", "THUMBS.DB", "desktop.ini"):
            (directory / name).write_bytes(b"OS metadata")
    for name in (".example", ".directory"):
        (skills / "code-review" / name).write_text("keep this resource")
install.install(list(build.HARNESSES), Path.home(), force=True)
"""
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=self.root,
            env={**os.environ, "HOME": str(self.home)}, capture_output=True, text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in (".DS_Store", "Thumbs.db", "ehthumbs.db", "Desktop.ini", "THUMBS.DB", "desktop.ini"):
            self.assertNotIn(name, result.stdout)
            self.assertEqual(list(self.home.rglob(name)), [])
        for directory in (".agents/skills", ".claude/skills", ".config/opencode/skills"):
            for name in (".example", ".directory"):
                self.assertEqual(
                    (self.home / directory / "code-review" / name).read_text(),
                    "keep this resource",
                )

    def test_os_metadata_does_not_trigger_reinstallation(self):
        self.install("--all")
        names = (".DS_Store", "Thumbs.db", "ehthumbs.db", "Desktop.ini", "THUMBS.DB", "desktop.ini")
        for directory in (".agents/skills", ".claude/skills", ".config/opencode/skills"):
            skills = self.home / directory
            for name in names:
                (skills / name).write_bytes(b"OS metadata")
                (skills / "code-review" / name).write_bytes(b"OS metadata")
        for name in names:
            (self.root / "source/skills" / name).write_bytes(b"Different metadata")
            (self.root / "source/skills/code-review" / name).write_bytes(b"Different metadata")

        result = self.install("--all")

        for name in names:
            self.assertNotIn(name, result.stdout)
        self.assertNotIn("Installed:", result.stdout)
        self.assertNotIn("Backed up:", result.stdout)
        self.assertFalse((self.home / ".ai-agents-backups").exists())

    def test_changed_files_are_backed_up_and_unchanged_files_are_skipped(self):
        self.install("claude")
        agent = self.home / ".claude/agents/docs-fetcher.md"
        generated = agent.read_text()
        agent.write_text("local edit")

        result = self.install("claude")

        self.assertEqual(agent.read_text(), generated)
        backups = list((self.home / ".ai-agents-backups").glob("*/.claude/agents/docs-fetcher.md"))
        self.assertEqual([path.read_text() for path in backups], ["local edit"])
        self.assertEqual(result.stdout.count("Backed up:"), 1)
        self.assertEqual(result.stdout.count("Installed:"), 1)

    def test_content_comparison_checks_bytes_and_extra_skill_files(self):
        self.install("claude")
        source = self.root / "build/claude/agents/docs-fetcher.md"
        agent = self.home / ".claude/agents/docs-fetcher.md"
        changed = b"x" * source.stat().st_size
        agent.write_bytes(changed)
        os.utime(agent, ns=(source.stat().st_atime_ns, source.stat().st_mtime_ns))
        extra = self.home / ".claude/skills/code-review/.local-notes"
        extra.write_text("keep these notes")

        result = self.install("claude")

        self.assertEqual(agent.read_bytes(), source.read_bytes())
        self.assertFalse(extra.exists())
        backups = list((self.home / ".ai-agents-backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / ".claude/agents/docs-fetcher.md").read_bytes(), changed)
        self.assertEqual(
            (backups[0] / ".claude/skills/code-review/.local-notes").read_text(),
            "keep these notes",
        )
        self.assertEqual(result.stdout.count("Backed up:"), 2)

    def test_repeated_replacements_keep_separate_backups(self):
        self.install("claude")
        agent = self.home / ".claude/agents/docs-fetcher.md"
        for content in ("first edit", "second edit"):
            agent.write_text(content)
            self.install("claude")

        backups = list((self.home / ".ai-agents-backups").glob("*/.claude/agents/docs-fetcher.md"))
        self.assertEqual(sorted(path.read_text() for path in backups), ["first edit", "second edit"])

    def test_replacement_confirmation_and_eof(self):
        self.install("claude")
        agent = self.home / ".claude/agents/docs-fetcher.md"
        generated = agent.read_text()
        agent.write_text("local edit")

        for answer in ("", "\n", "n\n"):
            with self.subTest(answer=answer):
                result = self.run_install("claude", force=False, input_text=answer)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Skipped:", result.stdout)
                self.assertEqual(agent.read_text(), "local edit")
                self.assertFalse((self.home / ".ai-agents-backups").exists())

        result = self.run_install("claude", force=False, input_text="YES\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(agent.read_text(), generated)
        backups = list((self.home / ".ai-agents-backups").glob("*/.claude/agents/docs-fetcher.md"))
        self.assertEqual([path.read_text() for path in backups], ["local edit"])

    def test_replaced_symlinks_are_backed_up_without_changing_targets(self):
        destination = self.home / ".claude/CLAUDE.md"
        destination.parent.mkdir()
        for existing in (True, False):
            with self.subTest(existing=existing):
                target = self.home / f"original-{existing}.md"
                if existing:
                    target.write_text("keep target")
                destination.symlink_to(target)

                self.install("claude")

                self.assertFalse(destination.is_symlink())
                self.assertEqual(
                    destination.read_bytes(), (self.root / "source/prompts/AGENTS.md").read_bytes(),
                )
                backups = [
                    directory / ".claude/CLAUDE.md"
                    for directory in (self.home / ".ai-agents-backups").iterdir()
                ]
                self.assertTrue(any(path.is_symlink() and path.readlink() == target for path in backups))
                if existing:
                    self.assertEqual(target.read_text(), "keep target")
                else:
                    self.assertFalse(target.exists())
                destination.unlink()

    def test_file_directory_conflicts_are_backed_up(self):
        base = self.home / ".claude/CLAUDE.md/local.md"
        base.parent.mkdir(parents=True)
        base.write_text("local directory")
        skill = self.home / ".claude/skills/code-review"
        skill.parent.mkdir()
        skill.write_text("local file")

        self.install("claude")

        self.assertTrue(base.parent.is_file())
        self.assertTrue((skill / "SKILL.md").is_file())
        backups = list((self.home / ".ai-agents-backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / ".claude/CLAUDE.md/local.md").read_text(), "local directory")
        self.assertEqual((backups[0] / ".claude/skills/code-review").read_text(), "local file")

    def test_all_harnesses_install_shared_skills_and_prompt_modes(self):
        for args in (("--all",), ("--all", "--work")):
            with self.subTest(args=args):
                self.install(*args)
                for directory in (".config/opencode/skills", ".claude/skills", ".agents/skills"):
                    for skill in (self.root / "source/skills").glob("*/SKILL.md"):
                        self.assertTrue((self.home / directory / skill.parent.name / "SKILL.md").is_file())
                    for mode in ("brainstorming", "thorough-plan"):
                        self.assertTrue((self.home / directory / mode / "SKILL.md").is_file())
                    self.assertFalse((self.home / directory / "brainstorm-with-agent").exists())
                    self.assertFalse((self.home / directory / "receiving-code-review").exists())
                opencode = self.home / ".config/opencode"
                self.assertTrue((opencode / "agents/brainstorm.md").is_file())
                self.assertFalse((opencode / "agents/thorough-plan.md").exists())
                self.assertFalse((opencode / "commands/code-full-review.md").exists())
                for legacy in ("agent", "command", "skill"):
                    self.assertFalse((opencode / legacy).exists())
                self.assertTrue((self.home / ".codex/agents/brainstorm.toml").is_file())
                self.assertTrue((self.home / ".claude/agents/brainstorm.md").is_file())

    def test_merged_review_skill_installs_without_removing_retired_or_unrelated_skills(self):
        directories = (".agents/skills", ".claude/skills", ".config/opencode/skills")
        for directory in directories:
            for name in ("receiving-code-review", "my-own-skill"):
                path = self.home / directory / name / "SKILL.md"
                path.parent.mkdir(parents=True)
                path.write_text(f"keep {name}\n")

        self.install("--all")

        source = self.root / "source/skills/code-review"
        for directory in directories:
            with self.subTest(directory=directory):
                for filename in ("SKILL.md", "feedback.md"):
                    self.assertEqual(
                        (self.home / directory / "code-review" / filename).read_bytes(),
                        (source / filename).read_bytes(),
                    )
                for name in ("receiving-code-review", "my-own-skill"):
                    self.assertEqual(
                        (self.home / directory / name / "SKILL.md").read_text(),
                        f"keep {name}\n",
                    )
        self.assertFalse((self.home / ".ai-agents-backups").exists())

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
                self.assertTrue((self.home / ".codex/agents/code-security.toml").is_file())
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

    def test_options_can_be_mixed_with_harnesses_and_provider_is_forwarded(self):
        result = self.install("claude", "--opencode-provider", "opencode", "opencode")

        self.assertNotIn("Which harnesses", result.stdout)
        self.assertTrue((self.home / ".claude/CLAUDE.md").is_file())
        self.assertIn(
            "model: opencode/",
            (self.home / ".config/opencode/agents/brainstorm.md").read_text(),
        )
        self.assertFalse((self.home / ".codex").exists())

    def test_local_context_is_opt_in_and_created_privately(self):
        local = self.home / ".config/ai-agents/local.md"
        self.install("codex")
        self.assertFalse(local.exists())

        result = self.install("codex", "--init-local")
        self.assertTrue(local.is_file())
        self.assertEqual(local.stat().st_mode & 0o777, 0o600)
        self.assertIn("Created local context:", result.stdout)

        local.write_text("My approved work context")
        self.install("codex")
        result = self.install("codex", "--init-local")
        self.assertEqual(local.read_text(), "My approved work context")
        self.assertIn("Preserved existing local context:", result.stdout)

    def test_init_local_preserves_directory_and_dangling_symlink(self):
        local = self.home / ".config/ai-agents/local.md"
        local.mkdir(parents=True)
        sentinel = local / "keep.md"
        sentinel.write_text("keep")
        self.install("codex", "--init-local")
        self.assertEqual(sentinel.read_text(), "keep")

        sentinel.unlink()
        local.rmdir()
        target = self.home / "must-not-create.md"
        local.symlink_to(target)
        self.install("codex", "--init-local")
        self.assertTrue(local.is_symlink())
        self.assertFalse(target.exists())

    def local_repository(self, startup=True):
        source = self.home.parent / "sample-wiki.git"
        source.mkdir()
        subprocess.run(["git", "init", "--quiet", str(source)], check=True)
        (source / ("AGENTS.md" if startup else "README.md")).write_text("Wiki source")
        subprocess.run(["git", "-C", str(source), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(source), "-c", "user.name=Test", "-c",
             "user.email=test@example.invalid", "-c", "commit.gpgsign=false",
             "commit", "--quiet", "-m", "Seed"], check=True,
        )
        return source

    def test_clone_and_init_link_new_local_context(self):
        source = self.local_repository()
        self.install("codex", "--clone-repo", str(source), "--init-local")
        checkout = self.home / "Knowledge/sample-wiki"
        self.assertEqual((checkout / "AGENTS.md").read_text(), "Wiki source")
        local = self.home / ".config/ai-agents/local.md"
        self.assertIn("~/Knowledge/sample-wiki/AGENTS.md", local.read_text())
        self.assertEqual(local.stat().st_mode & 0o777, 0o600)

        (checkout / "AGENTS.md").write_text("uncommitted change")
        result = self.run_install("codex", "--clone-repo", str(source), "--init-local")
        self.assertEqual(result.returncode, 1)
        self.assertEqual((checkout / "AGENTS.md").read_text(), "uncommitted change")

    def test_clone_without_init_leaves_local_context_absent(self):
        source = self.local_repository()
        self.install("codex", "--clone-repo", str(source))
        self.assertFalse((self.home / ".config/ai-agents/local.md").exists())
        self.assertTrue((self.home / "Knowledge/sample-wiki/AGENTS.md").is_file())

    def test_clone_accepts_current_directory_and_trailing_dot(self):
        source = self.local_repository()
        for index, path in enumerate((".", str(source) + "/.")):
            with self.subTest(path=path):
                home = self.home / str(index)
                home.mkdir()
                result = subprocess.run(
                    [sys.executable, str(self.root / "install.py"), "codex",
                     "--clone-repo", path, "--init-local", "--force"],
                    cwd=source, env={**os.environ, "HOME": str(home)},
                    capture_output=True, text=True, input="",
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                checkout = home / "Knowledge/sample-wiki"
                self.assertEqual((checkout / "AGENTS.md").read_text(), "Wiki source")
                self.assertIn("sample-wiki/AGENTS.md", (home / ".config/ai-agents/local.md").read_text())

    def test_invalid_build_options_do_not_clone_and_corrected_retry_succeeds(self):
        source = self.local_repository()
        result = self.run_install(
            "opencode", "--work", "--opencode-provider", "openai",
            "--clone-repo", str(source), "--init-local",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("--work cannot be combined", result.stderr)
        self.assertFalse((self.home / ".config/ai-agents").exists())
        self.assertFalse((self.home / ".config/opencode").exists())
        self.install("opencode", "--work", "--clone-repo", str(source), "--init-local")

    def test_clone_preserves_existing_context(self):
        source = self.local_repository(startup=False)
        local = self.home / ".config/ai-agents/local.md"
        local.parent.mkdir(parents=True)
        local.write_text("Approved work context")
        self.install("codex", "--clone-repo", str(source), "--init-local")
        self.assertEqual(local.read_text(), "Approved work context")
        local.unlink()
        self.install("codex", "--init-local")
        self.assertNotIn("For shared knowledge, read", local.read_text())

    def test_clone_configures_pointer_before_entry_point_exists(self):
        source = self.local_repository(startup=False)
        self.install("codex", "--clone-repo", str(source), "--init-local")
        local = self.home / ".config/ai-agents/local.md"
        self.assertIn("~/Knowledge/sample-wiki/AGENTS.md", local.read_text())

    def test_clone_refuses_symlink_destination(self):
        source = self.local_repository()
        target = self.home / "keep"
        target.mkdir()
        (target / "sentinel").write_text("keep")
        destination = self.home / "Knowledge/sample-wiki"
        destination.parent.mkdir(parents=True)
        destination.symlink_to(target, target_is_directory=True)
        result = self.run_install("codex", "--clone-repo", str(source))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(destination.is_symlink())
        self.assertEqual((target / "sentinel").read_text(), "keep")
        self.assertFalse((target / ".git").exists())

    def test_clone_failure_initializes_local_context_without_installing(self):
        result = self.run_install("codex", "--clone-repo", str(self.home / "missing.git"), "--init-local")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.home / ".codex").exists())
        local = self.home / ".config/ai-agents/local.md"
        self.assertTrue(local.is_file())
        self.assertIn("~/Knowledge/missing/AGENTS.md", local.read_text())
        self.assertNotIn("<repo-name>", local.read_text())
        self.assertIn("Git clone failed", result.stderr)

    def test_bare_installer_prompts_for_local_context_and_repository(self):
        source = self.local_repository()
        result = self.run_install(force=False, input_text=f"\ny\n{source}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Create machine-local context", result.stdout)
        self.assertIn("Repository URL or path to clone", result.stdout)
        self.assertIn("sample-wiki/AGENTS.md", (self.home / ".config/ai-agents/local.md").read_text())

    def test_bare_installer_can_skip_optional_setup(self):
        result = self.run_install(force=False, input_text="\nn\n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.home / ".config/ai-agents").exists())

    def test_help_and_invalid_arguments_write_nothing(self):
        cases = (
            (("--help",), 0), (("-h",), 0), (("--bogus",), 2), (("unknown",), 2),
            (("--opencode-provider",), 2), (("codex", "codex"), 1),
            (("opencode", "--work", "--opencode-provider", "openai"), 1),
        )
        for args, code in cases:
            with self.subTest(args=args):
                result = self.run_install(*args, force=False)
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                self.assertFalse((self.root / "build").exists())
                self.assertEqual(list(self.home.iterdir()), [])

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

    def init_antigravity(self, *args, input_text=None):
        shutil.copy2(REPO / "antigravity-init.py", self.root / "antigravity-init.py")
        env = {
            key: value for key, value in os.environ.items()
            if key not in {"GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_CONFIG_NOSYSTEM", "XDG_CONFIG_HOME"}
        }
        env["HOME"] = str(self.home)
        return subprocess.run(
            [sys.executable, "antigravity-init.py", *args],
            cwd=self.root, env=env,
            capture_output=True, text=True,
            input=input_text,
            stdin=subprocess.DEVNULL if input_text is None else None,
        )

    def seed_external_gitconfig(self):
        dotfiles = self.home / "dotfiles/git"
        dotfiles.mkdir(parents=True)
        included = dotfiles / "gitconfig"
        excludes = dotfiles / "gitignore_global"
        included.write_text(f"[core]\n    excludesfile = {excludes}\n")
        excludes.write_text(".DS_Store\n")
        (self.home / ".gitconfig").write_text(f"[include]\n    path = {included}\n")
        return included.resolve(), excludes.resolve()

    def test_antigravity_init_help_and_unknown_options_write_nothing(self):
        config = self.home / ".gemini/antigravity-cli/settings.json"
        for args, code in ((("--help",), 0), (("-h",), 0), (("--bogus",), 2)):
            with self.subTest(args=args):
                result = self.init_antigravity(*args)
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                self.assertIn("usage:", (result.stdout + result.stderr).lower())
                self.assertFalse(config.exists())

    def test_antigravity_init_detects_external_git_files_and_merges_existing_settings(self):
        included, excludes = self.seed_external_gitconfig()
        config = self.home / ".gemini/antigravity-cli/settings.json"
        config.parent.mkdir(parents=True)
        original = json.dumps({
            "trustedWorkspaces": ["/tmp/work"],
            "permissions": {"allow": ["command(git status)"], "deny": ["read_file(.env)"]},
        }) + "\n"
        config.write_text(original)

        result = self.init_antigravity("--yes")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        updated = json.loads(config.read_text())
        self.assertEqual(updated["trustedWorkspaces"], ["/tmp/work"])
        self.assertEqual(updated["permissions"]["deny"], ["read_file(.env)"])
        self.assertEqual(
            updated["permissions"]["allow"],
            [
                "command(git status)",
                f"read_file({included.as_posix()})",
                f"read_file({excludes.as_posix()})",
            ],
        )
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        backups = list((self.home / ".ai-agents-backups").glob("antigravity-*/settings.json"))
        self.assertEqual([path.read_text() for path in backups], [original])
        self.assertEqual(backups[0].stat().st_mode & 0o777, 0o600)
        self.assertEqual(backups[0].parent.stat().st_mode & 0o777, 0o700)

    def test_antigravity_init_without_confirmation_preserves_existing_settings(self):
        self.seed_external_gitconfig()
        config = self.home / ".gemini/antigravity-cli/settings.json"
        config.parent.mkdir(parents=True)
        config.write_text('{"model": "keep"}\n')

        result = self.init_antigravity()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(config.read_text(), '{"model": "keep"}\n')
        self.assertFalse((self.home / ".ai-agents-backups").exists())

    def test_antigravity_init_refuses_symlinks_and_skips_unchanged(self):
        included, excludes = self.seed_external_gitconfig()
        config = self.home / ".gemini/antigravity-cli/settings.json"
        config.parent.mkdir(parents=True)
        target = self.home / "other.json"
        for existing in (True, False):
            with self.subTest(existing=existing):
                if existing:
                    target.write_text("keep me")
                config.symlink_to(target)
                result = self.init_antigravity("--yes")
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(config.is_symlink())
                if existing:
                    self.assertEqual(target.read_text(), "keep me")
                    target.unlink()
                else:
                    self.assertFalse(target.exists())
                config.unlink()

        extra = self.home / "shared/docs"
        extra.mkdir(parents=True)
        result = self.init_antigravity("--allow-read", str(extra))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(config.read_text())
        self.assertEqual(
            data["permissions"]["allow"],
            [
                f"read_file({included.as_posix()})",
                f"read_file({excludes.as_posix()})",
                f"read_file({extra.resolve().as_posix()})",
            ],
        )
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        config.chmod(0o644)

        repeat = self.init_antigravity("--allow-read", str(extra))
        self.assertEqual(repeat.returncode, 0, repeat.stdout + repeat.stderr)
        self.assertIn("Unchanged:", repeat.stdout)
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.home / ".ai-agents-backups").exists())

    def test_antigravity_init_no_external_gitconfig_writes_nothing(self):
        (self.home / ".gitconfig").write_text("[user]\n    name = Test\n")
        config = self.home / ".gemini/antigravity-cli/settings.json"

        result = self.init_antigravity()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("nothing to add", result.stdout)
        self.assertFalse(config.exists())


if __name__ == "__main__":
    unittest.main()
