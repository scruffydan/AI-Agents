from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from ai_agents.domain.options import InstallOptions
from ai_agents.install.service import install_project
from tests.helpers import repo_root


class InstallServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = repo_root()

    def test_install_project_installs_all_harnesses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_dir = temp_root / "build"
            home_dir = temp_root / "home"
            report = install_project(
                InstallOptions(
                    repo_root=self.repo_root,
                    build_dir=build_dir,
                    selected_harnesses=("opencode", "claude", "codex"),
                    environment="default",
                    force=True,
                    home_dir=home_dir,
                ),
                prompt=lambda _: "y",
            )

            self.assertEqual([spec.name for spec in report.harnesses], ["opencode", "claude", "codex"])
            self.assertTrue((home_dir / ".config" / "opencode" / "agent" / "code-security.md").exists())
            self.assertTrue((home_dir / ".claude" / "agents" / "code-security.md").exists())
            self.assertTrue((home_dir / ".codex" / "agents" / "code-security.toml").exists())
            self.assertTrue((home_dir / ".agents" / "skills" / "command-code-full-review" / "SKILL.md").exists())
            self.assertTrue((home_dir / ".codex" / "AGENTS.md").exists())

    def test_install_project_supports_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_dir = temp_root / "build"
            home_dir = temp_root / "home"

            report = install_project(
                InstallOptions(
                    repo_root=self.repo_root,
                    build_dir=build_dir,
                    selected_harnesses=("opencode",),
                    selected_components=("base", "skills"),
                    environment="default",
                    dry_run=True,
                    force=True,
                    home_dir=home_dir,
                ),
                prompt=lambda _: "y",
            )

            self.assertTrue(report.dry_run)
            self.assertEqual(len(report.installed_targets), 0)
            self.assertEqual([action.component for action in report.plan.actions], ["base", "skills"])
            self.assertFalse((home_dir / ".config" / "opencode").exists())

    def test_install_project_can_filter_components(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_dir = temp_root / "build"
            home_dir = temp_root / "home"

            report = install_project(
                InstallOptions(
                    repo_root=self.repo_root,
                    build_dir=build_dir,
                    selected_harnesses=("claude",),
                    selected_components=("skills",),
                    environment="default",
                    force=True,
                    home_dir=home_dir,
                ),
                prompt=lambda _: "y",
            )

            self.assertEqual([action.component for action in report.plan.actions], ["skills"])
            self.assertEqual([Path(target).resolve() for target in report.installed_targets], [(home_dir / ".claude" / "skills").resolve()])
            self.assertFalse((home_dir / ".claude" / "CLAUDE.md").exists())
            self.assertTrue((home_dir / ".claude" / "skills" / "git-commit" / "SKILL.md").exists())

    def test_install_project_executes_planned_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_dir = temp_root / "build"
            home_dir = temp_root / "home"

            report = install_project(
                InstallOptions(
                    repo_root=self.repo_root,
                    build_dir=build_dir,
                    selected_harnesses=("opencode",),
                    selected_components=("base", "skills"),
                    environment="default",
                    force=True,
                    home_dir=home_dir,
                ),
                prompt=lambda _: "y",
            )

            planned_destinations = [str(action.destination) for action in report.plan.actions if action.status == "ready"]
            self.assertEqual(list(report.installed_targets), planned_destinations)
