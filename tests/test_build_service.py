from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from ai_agents.build.service import build_project
from ai_agents.domain.options import BuildOptions
from tests.helpers import repo_root


class BuildServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = repo_root()

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

            self.assertGreater(report.document_count, 0)
            self.assertTrue((output_dir / "opencode" / "agent" / "code-security.md").exists())
            self.assertTrue((output_dir / "claude" / "agents" / "code-security.md").exists())
            self.assertFalse((output_dir / "claude" / "commands" / "brainstorm.md").exists())
            self.assertTrue((output_dir / "codex" / ".codex" / "agents" / "code-security.toml").exists())
            self.assertTrue((output_dir / "codex" / ".agents" / "skills" / "command-code-full-review" / "SKILL.md").exists())
            self.assertTrue((output_dir / "codex" / ".agents" / "skills" / "git-commit" / "SKILL.md").exists())
            self.assertTrue((output_dir / "codex" / "AGENTS.md").exists())
            self.assertEqual(report.manifest_path.resolve(), (output_dir / "manifest.json").resolve())

            manifest = json.loads((output_dir / "manifest.json").read_text())
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(manifest["environment"], "default")
            self.assertEqual(manifest["harnesses"], ["opencode", "claude", "codex"])
            self.assertIn("source/prompts/code-security.md", manifest["documents"])

            opencode_security = next(
                artifact
                for artifact in manifest["artifacts"]
                if artifact["relative_output_path"] == "opencode/agent/code-security.md"
            )
            codex_skill = next(
                artifact
                for artifact in manifest["artifacts"]
                if artifact["relative_output_path"] == "codex/.agents/skills/git-commit"
            )
            codex_base = next(
                artifact
                for artifact in manifest["artifacts"]
                if artifact["relative_output_path"] == "codex/AGENTS.md"
            )

            self.assertEqual(opencode_security["component"], "documents")
            self.assertEqual(opencode_security["source_path"], "source/prompts/code-security.md")
            self.assertEqual(opencode_security["model_profile"], "deep_review")
            self.assertEqual(codex_skill["component"], "skills")
            self.assertEqual(codex_skill["source_path"], "source/skills/git-commit")
            self.assertIsNone(codex_skill["model_profile"])
            self.assertEqual(codex_base["component"], "base")

            self.assertNotIn("claude/commands/brainstorm.md", [artifact["relative_output_path"] for artifact in manifest["artifacts"]])
