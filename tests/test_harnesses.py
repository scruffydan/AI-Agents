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

    def test_opencode_mode_documents_use_agent_directory(self) -> None:
        spec = get_harness("opencode")

        self.assertEqual(spec.output_dir_for(DocumentKind.MODE), "agent")

    def test_harness_contract_exposes_component_paths(self) -> None:
        spec = get_harness("claude")

        self.assertEqual(spec.component_for_kind(DocumentKind.BASE), "base")
        self.assertEqual(spec.component_for_kind(DocumentKind.SUBAGENT), "documents")
        self.assertEqual(spec.component_for_kind(DocumentKind.SKILL), "skills")
        self.assertEqual(spec.base_output_path().as_posix(), "claude/CLAUDE.md")
        self.assertEqual(spec.skill_output_path("example").as_posix(), "claude/skills/example")

    def test_install_entries_can_be_filtered_by_component(self) -> None:
        spec = get_harness("codex")

        base_entries = spec.install_entries_for(("base",))
        skill_entries = spec.install_entries_for(("skills",))

        self.assertEqual([entry.label for entry in base_entries], ["codex base instructions"])
        self.assertEqual([entry.label for entry in skill_entries], ["codex skills"])

    def test_unknown_harness_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown harness"):
            get_harness("unknown")
