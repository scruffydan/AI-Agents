from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from ai_agents.build.service import build_project
from ai_agents.domain.options import BuildOptions


class BuildServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_build_project_writes_all_harness_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "build"
            report = build_project(
                BuildOptions(
                    repo_root=self.repo_root,
                    output_dir=output_dir,
                    selected_harnesses=("opencode", "claude", "codex"),
                    environment="default",
                )
            )

            self.assertEqual(report.document_count, 12)
            self.assertTrue((output_dir / "opencode" / "agent" / "code-security.md").exists())
            self.assertTrue((output_dir / "claude" / "agents" / "code-security.md").exists())
            self.assertTrue((output_dir / "claude" / "commands" / "brainstorm.md").exists())
            self.assertTrue((output_dir / "codex" / ".codex" / "agents" / "code-security.toml").exists())
            self.assertTrue((output_dir / "codex" / ".agents" / "skills" / "command-code-full-review" / "SKILL.md").exists())
            self.assertTrue((output_dir / "codex" / ".agents" / "skills" / "git-commit" / "SKILL.md").exists())
            self.assertTrue((output_dir / "codex" / "AGENTS.md").exists())
