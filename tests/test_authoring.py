"""Small end-to-end checks; every write stays in a temporary repository copy."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest


REPO = Path(__file__).resolve().parents[1]


class AuthoringTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("source", "templates"):
            shutil.copytree(REPO / name, self.root / name)
        for name in ("build.py", "new.py"):
            shutil.copy2(REPO / name, self.root / name)

    def cli(self, *args, success=True):
        result = subprocess.run(
            [sys.executable, *args], cwd=self.root, capture_output=True, text=True
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_one_agent_builds_for_all_harnesses_and_override_is_local(self):
        description = 'Review queries: include "slow" queries # database'
        self.cli("new.py", "agent", "database-review", "--description", description)
        source = self.root / "source/agents/database-review.md"
        body = 'Check C:\\queries and the literal delimiter """.\n{{include:_example.md}}'
        (self.root / "source/prompts/_example.md").write_text("Explain the result.")
        _, metadata, _ = source.read_text().split("+++", 2)
        source.write_text(f"+++{metadata}+++\n\n{body}")
        self.cli("build.py")
        codex = self.root / "build/codex/.codex/agents/database-review.toml"
        rendered = tomllib.loads(codex.read_text())
        self.assertEqual(rendered["description"], description)
        self.assertEqual(rendered["developer_instructions"].strip(),
                         body.replace("{{include:_example.md}}", "Explain the result."))
        claude = self.root / "build/claude/agents/database-review.md"
        opencode = self.root / "build/opencode/agents/database-review.md"
        for path in (claude, opencode):
            line = next(line for line in path.read_text().splitlines() if line.startswith("description: "))
            self.assertEqual(json.loads(line.removeprefix("description: ")), description)
        old_codex, old_opencode = codex.read_bytes(), opencode.read_bytes()
        template = (self.root / "templates/defaults/claude/agent.md").read_text()
        (self.root / "templates/overrides/claude/database-review.md").write_text(
            template.replace("tools: Read, Glob, Grep", "tools: Read")
        )
        self.cli("build.py")
        self.assertIn("tools: Read\n", claude.read_text())
        self.assertEqual(codex.read_bytes(), old_codex)
        self.assertEqual(opencode.read_bytes(), old_opencode)

    def test_selected_harnesses_and_shared_skill_folder(self):
        self.cli("new.py", "agent", "database-review", "--harness", "claude")
        self.cli("new.py", "skill", "database-debugging")
        skill = self.root / "source/skills/database-debugging"
        (skill / "example.sql").write_text("EXPLAIN SELECT 1;\n")
        self.cli("build.py")
        self.assertTrue((self.root / "build/claude/agents/database-review.md").exists())
        self.assertFalse((self.root / "build/opencode/agents/database-review.md").exists())
        self.assertFalse((self.root / "build/codex/.codex/agents/database-review.toml").exists())
        for target in ("claude/skills", "opencode/skills", "codex/.agents/skills"):
            for path in skill.iterdir():
                self.assertEqual(path.read_bytes(), (self.root / "build" / target / skill.name / path.name).read_bytes())
        self.cli("build.py", "claude")
        self.assertEqual([p.name for p in (self.root / "build").iterdir()], ["claude"])

    def test_creation_refuses_overwrites_and_bad_names_or_profiles(self):
        for kind, relative in (("agent", "source/agents/example.md"), ("skill", "source/skills/example/SKILL.md")):
            self.cli("new.py", kind, "example")
            path = self.root / relative
            original = path.read_bytes()
            self.cli("new.py", kind, "example", success=False)
            self.assertEqual(path.read_bytes(), original)
            self.cli("new.py", kind, "../outside", success=False)
        self.cli("new.py", "agent", "missing-profile", "--profile", "missing", success=False)
        self.assertFalse((self.root / "source/agents/missing-profile.md").exists())
        self.cli("new.py", "agent", "brainstorm", success=False)
        self.cli("new.py", "skill", "brainstorm-with-agent", success=False)

    def test_failed_build_preserves_previous_output(self):
        self.cli("build.py")
        output = self.root / "build"

        def snapshot():
            return {p.relative_to(output): p.read_bytes()
                    for p in output.rglob("*") if p.is_file()}

        original = snapshot()
        cases = (
            ("templates/claude/agents/broken.md", "{{prompt:missing}}", "Unknown prompt"),
            ("templates/codex/.codex/agents/explore.toml",
             (output / "codex/.codex/agents/explore.toml").read_text(), "Duplicate output"),
            ("templates/claude/skills/git-commit/SKILL.md", "conflict", "Duplicate output"),
            ("templates/claude/skills/git-commit", "directory conflict", "Duplicate output"),
            ("templates/codex/.codex/agents/explore.toml/extra.md", "ancestor conflict", "Duplicate output"),
        )
        for relative, content, error in cases:
            with self.subTest(path=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                result = self.cli("build.py", success=False)
                self.assertIn(error, result.stderr)
                self.assertEqual(snapshot(), original)
                path.unlink()
                # Remove temporary directories so later cases can test file conflicts.
                parent = path.parent
                while parent != self.root and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent

    def test_unicode_descriptions_are_portable_yaml(self):
        description = "Review queries 🔍\u0085\u2028\u2029"
        expected = 'description: "Review queries 🔍\\u0085\\u2028\\u2029"\n'
        self.cli("new.py", "agent", "unicode-agent", "--description", description)
        self.cli("new.py", "skill", "unicode-skill", "--description", description)
        self.cli("build.py")

        targets = (
            "claude/agents/unicode-agent.md",
            "opencode/agents/unicode-agent.md",
            "claude/skills/unicode-skill/SKILL.md",
            "opencode/skills/unicode-skill/SKILL.md",
            "codex/.agents/skills/unicode-skill/SKILL.md",
        )
        for target in targets:
            with self.subTest(target=target):
                self.assertIn(expected, (self.root / "build" / target).read_text())
        codex = self.root / "build/codex/.codex/agents/unicode-agent.toml"
        self.assertEqual(tomllib.loads(codex.read_text())["description"], description)

    def test_finder_metadata_is_ignored_without_disabling_override_validation(self):
        for relative in ("templates/overrides/.DS_Store",
                         "templates/overrides/claude/.DS_Store",
                         "templates/claude/agents/.DS_Store"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"\x00\xffFinder metadata")
        self.cli("build.py", "codex")
        self.cli("build.py")
        self.assertFalse((self.root / "build/claude/agents/.DS_Store").exists())

        (self.root / "templates/overrides/claude/nonexistent.md").write_text("bad override")
        result = self.cli("build.py", success=False)
        self.assertIn("Override has no matching agent", result.stderr)


if __name__ == "__main__":
    unittest.main()
