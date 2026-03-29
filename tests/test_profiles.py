from __future__ import annotations

from pathlib import Path
import unittest

from ai_agents.profiles.resolver import load_model_profiles, resolve_model_profile
from tests.helpers import repo_root


class ProfileResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = repo_root()
        self.profiles = load_model_profiles(self.repo_root / "source" / "model-profiles.toml")

    def test_resolves_default_opencode_profile(self) -> None:
        resolved = resolve_model_profile(self.profiles, "default", "default", "opencode")

        self.assertEqual(resolved.model, "openai/gpt-5.4")
        self.assertEqual(resolved.settings["reasoning_effort"], "medium")

    def test_resolves_work_profile(self) -> None:
        resolved = resolve_model_profile(self.profiles, "deep_review", "work", "opencode")

        self.assertEqual(resolved.model, "google-vertex-anthropic/claude-opus-4-5@20251101")
        self.assertEqual(resolved.settings["reasoning_effort"], "high")

    def test_applies_shared_profile_settings_to_other_harnesses(self) -> None:
        resolved = resolve_model_profile(self.profiles, "creative", "default", "claude")

        self.assertEqual(resolved.model, "claude-opus-4-5")
        self.assertEqual(resolved.settings["reasoning_effort"], "high")
        self.assertEqual(resolved.settings["temperature"], 0.95)
        self.assertEqual(resolved.settings["top_p"], 0.92)

    def test_harness_specific_settings_override_shared_defaults(self) -> None:
        profiles = {
            "example": {
                "shared": {"reasoning_effort": "medium", "temperature": 0.2},
                "default": {
                    "opencode": {"provider": "openai", "model": "gpt-5.4", "temperature": 0.8},
                },
            }
        }

        resolved = resolve_model_profile(profiles, "example", "default", "opencode")

        self.assertEqual(resolved.settings["reasoning_effort"], "medium")
        self.assertEqual(resolved.settings["temperature"], 0.8)

    def test_raises_on_unknown_profile(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown model profile"):
            resolve_model_profile(self.profiles, "missing", "default", "opencode")

    def test_raises_on_missing_harness_entry(self) -> None:
        profiles = {"default": {"default": {"opencode": {"provider": "openai", "model": "gpt-5.4"}}}}

        with self.assertRaisesRegex(ValueError, "missing profile entry"):
            resolve_model_profile(profiles, "default", "default", "claude")

    def test_raises_on_invalid_shared_profile_settings(self) -> None:
        profiles = {
            "default": {"shared": "invalid", "default": {"opencode": {"provider": "openai", "model": "gpt-5.4"}}}
        }

        with self.assertRaisesRegex(ValueError, "shared settings must be a table"):
            resolve_model_profile(profiles, "default", "default", "opencode")

    def test_raises_when_opencode_provider_is_missing(self) -> None:
        profiles = {"default": {"default": {"opencode": {"model": "gpt-5.4"}}}}

        with self.assertRaisesRegex(ValueError, "must define a non-empty provider"):
            resolve_model_profile(profiles, "default", "default", "opencode")

    def test_raises_when_opencode_model_uses_composed_string(self) -> None:
        profiles = {"default": {"default": {"opencode": {"provider": "openai", "model": "openai/gpt-5.4"}}}}

        with self.assertRaisesRegex(ValueError, "must use split provider/model fields"):
            resolve_model_profile(profiles, "default", "default", "opencode")

    def test_raises_when_non_opencode_profile_uses_provider(self) -> None:
        profiles = {"default": {"default": {"claude": {"provider": "openai", "model": "claude-sonnet-4-6"}}}}

        with self.assertRaisesRegex(ValueError, "does not support provider"):
            resolve_model_profile(profiles, "default", "default", "claude")
