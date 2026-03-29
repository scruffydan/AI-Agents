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
