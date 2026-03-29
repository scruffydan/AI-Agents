from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from ai_agents.content.schema import parse_document
from ai_agents.content.validation import validate_document
from ai_agents.domain.harnesses import get_harness
from ai_agents.profiles.resolver import load_model_profiles, resolve_model_profile
from ai_agents.render import claude as render_claude
from ai_agents.render.opencode import render_document
from tests.helpers import fixtures_dir, repo_root


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = repo_root()
        self.fixtures = fixtures_dir()
        self.profiles = load_model_profiles(self.repo_root / "source" / "model-profiles.toml")

    def test_parses_valid_harness_neutral_document(self) -> None:
        document = parse_document(self.fixtures / "source" / "security-review.md")

        self.assertEqual(document.name, "security-review")
        self.assertEqual(document.model_profile, "deep_review")
        self.assertEqual(set(document.targets), {"opencode"})
        self.assertEqual(document.targets["opencode"].metadata["permission"]["edit"], "deny")

    def test_validate_and_render_opencode_golden(self) -> None:
        document = parse_document(self.fixtures / "source" / "security-review.md")
        validate_document(document)
        resolved = resolve_model_profile(self.profiles, document.model_profile, "default", "opencode")

        artifact = render_document(document, resolved, harness=get_harness("opencode"))

        self.assertIsNotNone(artifact)
        self.assertEqual(artifact.relative_path, "opencode/agent/security-review.md")
        expected = (self.fixtures / "expected" / "opencode" / "agent" / "security-review.md").read_text()
        self.assertEqual(artifact.content, expected)

    def test_opencode_render_normalizes_reasoning_key(self) -> None:
        document = parse_document(self.fixtures / "source" / "security-review.md")
        resolved = resolve_model_profile(self.profiles, document.model_profile, "default", "opencode")

        artifact = render_document(document, resolved, harness=get_harness("opencode"))

        self.assertIsNotNone(artifact)
        self.assertIn("reasoningEffort", artifact.content)
        self.assertNotIn("reasoning_effort", artifact.content)

    def test_opencode_command_omits_reasoning_setting(self) -> None:
        document = parse_document(self.repo_root / "source" / "prompts" / "code-full-review.md")
        resolved = resolve_model_profile(self.profiles, document.model_profile, "default", "opencode")

        artifact = render_document(document, resolved, harness=get_harness("opencode"))

        self.assertIsNotNone(artifact)
        self.assertIn("model: openai/gpt-5.4", artifact.content)
        self.assertNotIn("reasoningEffort", artifact.content)

    def test_claude_subagent_uses_full_model_without_implicit_effort(self) -> None:
        document = parse_document(self.repo_root / "source" / "prompts" / "code-security.md")
        resolved = resolve_model_profile(self.profiles, document.model_profile, "default", "claude")

        artifact = render_claude.render_document(document, resolved, harness=get_harness("claude"))

        self.assertIsNotNone(artifact)
        self.assertIn("model: claude-opus-4-5", artifact.content)
        self.assertNotIn("model: opus", artifact.content)
        self.assertNotIn("effort:", artifact.content)

    def test_validate_rejects_unknown_metadata_key(self) -> None:
        document = parse_document(self.fixtures / "source" / "security-review.md")
        document.targets["opencode"].metadata["unsupported"] = True

        with self.assertRaisesRegex(ValueError, "does not support metadata keys"):
            validate_document(document)

    def test_parse_rejects_unsupported_shared_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "shared.md"
            path.write_text(
                "+++\n"
                'description = "Example"\n'
                'kind = "command"\n'
                'model_profile = "default"\n\n'
                "[shared]\n"
                'role = "unused"\n\n'
                "[targets.opencode]\n"
                "+++\n\n"
                "Hello\n"
            )

            with self.assertRaisesRegex(ValueError, r"field shared is not supported"):
                parse_document(path)

    def test_parse_rejects_unsupported_target_partials(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partials.md"
            path.write_text(
                "+++\n"
                'description = "Example"\n'
                'kind = "command"\n'
                'model_profile = "default"\n\n'
                "[targets.opencode]\n"
                'partials = ["shared-intro"]\n'
                "+++\n\n"
                "Hello\n"
            )

            with self.assertRaisesRegex(ValueError, r"field targets\.opencode\.partials is not supported"):
                parse_document(path)
