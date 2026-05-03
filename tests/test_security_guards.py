from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from ai_agents.build.service import build_project
from ai_agents.content.includes import expand_includes
from ai_agents.content.loader import load_documents
from ai_agents.domain.options import BuildOptions
from tests.helpers import repo_root


class SecurityGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = repo_root()

    def test_build_output_must_stay_within_build_directory(self) -> None:
        with self.assertRaisesRegex(ValueError, "output directory must stay within"):
            build_project(BuildOptions(repo_root=self.repo_root, output_dir=self.repo_root / "source"))

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "output directory must stay within"):
                build_project(BuildOptions(repo_root=self.repo_root, output_dir=Path(tmp) / "new-build"))

    def test_expand_includes_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            include_dir = temp_root / "includes"
            include_dir.mkdir()
            (temp_root / "secret.md").write_text("nope")

            with self.assertRaisesRegex(ValueError, "include path must stay within"):
                expand_includes("{{include:../secret.md}}", include_dir)

    def test_load_documents_rejects_symlinked_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            prompts_dir = temp_root / "prompts"
            prompts_dir.mkdir()

            real_prompt = temp_root / "real.md"
            real_prompt.write_text(
                "+++\n"
                'description = "Example"\n'
                'kind = "command"\n'
                'model_profile = "default"\n'
                "\n"
                "[targets.opencode]\n"
                "+++\n\n"
                "Hello\n"
            )
            os.symlink(real_prompt, prompts_dir / "linked.md")

            with self.assertRaisesRegex(ValueError, "symlinks are not allowed"):
                load_documents(prompts_dir, include_dir=prompts_dir)
