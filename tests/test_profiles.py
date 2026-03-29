from __future__ import annotations

from pathlib import Path
import unittest

from ai_agents.profiles.resolver import load_model_profiles, resolve_model_profile


class ProfileResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.profiles = load_model_profiles(self.repo_root / "source" / "model-profiles.toml")

    def test_resolves_default_opencode_profile(self) -> None:
        resolved = resolve_model_profile(self.profiles, "default", "default", "opencode")

        self.assertEqual(resolved.model, "openai/gpt-5.4")
        self.assertEqual(resolved.settings["reasoning_effort"], "medium")

    def test_resolves_work_profile(self) -> None:
        resolved = resolve_model_profile(self.profiles, "deep_review", "work", "opencode")

        self.assertEqual(resolved.model, "google-vertex-anthropic/claude-opus-4-5@20251101")
        self.assertEqual(resolved.settings["reasoning_effort"], "high")

    def test_raises_on_unknown_profile(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown model profile"):
            resolve_model_profile(self.profiles, "missing", "default", "opencode")

    def test_raises_on_missing_harness_entry(self) -> None:
        profiles = {"default": {"default": {"opencode": {"model": "openai/gpt-5.4"}}}}

        with self.assertRaisesRegex(ValueError, "missing profile entry"):
            resolve_model_profile(profiles, "default", "default", "claude")
