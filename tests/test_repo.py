from __future__ import annotations

from pathlib import Path
import unittest

from ai_agents.repo import find_repo_root


class RepoTests(unittest.TestCase):
    def test_find_repo_root_from_package_path(self) -> None:
        start = Path(__file__).resolve().parent / ".." / "ai_agents" / "cli.py"

        self.assertEqual(find_repo_root(start).resolve(), Path(__file__).resolve().parent.parent)
