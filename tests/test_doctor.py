from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from ai_agents.build.service import build_project
from ai_agents.doctor import render_doctor_report, run_doctor
from ai_agents.domain.options import BuildOptions
from tests.helpers import repo_root


class DoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = repo_root()

    def test_doctor_warns_when_manifest_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            (temp_root / "source").mkdir()
            (temp_root / "source" / "prompts").mkdir(parents=True)
            (temp_root / "source" / "prompts" / "AGENTS.md").write_text("Base\n")
            (temp_root / "source" / "prompts" / "test.md").write_text(
                "+++\n"
                'description = "Example"\n'
                'kind = "command"\n'
                'model_profile = "default"\n\n'
                '[targets.opencode]\n'
                "+++\n\n"
                "Hello\n"
            )
            (temp_root / "source" / "skills").mkdir()
            (temp_root / "source" / "model-profiles.toml").write_text(
                "[profiles.default.default.opencode]\nmodel = \"openai/gpt-5.5\"\n"
            )

            report = run_doctor(temp_root, verify_installed=False)

            self.assertTrue(report.ok)
            self.assertEqual(report.failures, [])
            self.assertEqual(len(report.warnings), 1)
            self.assertIn("build manifest not found", report.warnings[0].message)

    def test_doctor_validates_built_manifest(self) -> None:
        build_project(
            BuildOptions(
                repo_root=self.repo_root,
                selected_harnesses=("opencode", "claude", "codex"),
            )
        )

        report = run_doctor(self.repo_root, verify_installed=False)

        self.assertTrue(report.ok)
        self.assertEqual(report.failures, [])

    def test_doctor_reports_installed_failures(self) -> None:
        report = run_doctor(self.repo_root, verify_installed=True, home_dir=Path("/tmp/nonexistent-ai-agents-home"))

        self.assertFalse(report.ok)
        self.assertTrue(any(issue.scope == "installed" for issue in report.failures))

    def test_rendered_report_mentions_failures(self) -> None:
        report = run_doctor(self.repo_root, verify_installed=True, home_dir=Path("/tmp/nonexistent-ai-agents-home"))

        rendered = render_doctor_report(report)

        self.assertIn("Failures:", rendered)
        self.assertIn("missing installed targets", rendered)

    def test_json_output_shape(self) -> None:
        report = run_doctor(self.repo_root, verify_installed=False)

        payload = json.loads(json.dumps(report.to_dict()))

        self.assertIn("repo_root", payload)
        self.assertIn("checked", payload)
        self.assertIn("warnings", payload)
        self.assertIn("failures", payload)
        self.assertIn("ok", payload)
