from __future__ import annotations

import unittest

from ai_agents.domain.documents import DocumentKind
from ai_agents.domain.harnesses import get_harness, select_harnesses


class HarnessRegistryTests(unittest.TestCase):
    def test_default_selection_is_opencode_only(self) -> None:
        selected = select_harnesses((), include_all=False)

        self.assertEqual([spec.name for spec in selected], ["opencode"])

    def test_all_selection_returns_every_registered_harness(self) -> None:
        selected = select_harnesses((), include_all=True)

        self.assertEqual([spec.name for spec in selected], ["opencode", "claude", "codex"])

    def test_opencode_supports_modes(self) -> None:
        spec = get_harness("opencode")

        self.assertTrue(spec.supports_modes)
        self.assertEqual(spec.output_dir_for(DocumentKind.MODE), "agent")

    def test_unknown_harness_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown harness"):
            get_harness("unknown")
