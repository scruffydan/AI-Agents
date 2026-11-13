"""Offline checks for upstream pin discovery; no test contacts GitHub."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SHA_A = "a" * 40
SHA_B = "b" * 40


class UpstreamPinTests(unittest.TestCase):
    def list_pins(self, root):
        return subprocess.run(
            [sys.executable, str(root / "upstream.py"), "--list"],
            cwd=root,
            capture_output=True,
            text=True,
        )

    def test_every_adapted_skill_cites_one_consistent_pin(self):
        result = self.list_pins(REPO)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for license_file in sorted((REPO / "source/skills").glob("*/LICENSE")):
            skill = license_file.parent.relative_to(REPO).as_posix()
            self.assertIn(f"{skill}/SKILL.md", result.stdout)

    def test_conflicting_pins_fail_and_branch_links_are_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copy2(REPO / "upstream.py", root / "upstream.py")
            link = "https://github.com/owner/repo/blob/{}/skills/x/SKILL.md"
            (root / "README.md").write_text(f"[x]({link.format(SHA_A)})\n")
            (root / "THIRD_PARTY_NOTICES.md").write_text(
                f"[x]({link.format(SHA_B)})\n[y]({link.format('main')})\n"
            )

            result = self.list_pins(root)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("skills/x/SKILL.md has different pins", result.stderr)
        self.assertNotIn("main", result.stdout)


if __name__ == "__main__":
    unittest.main()
