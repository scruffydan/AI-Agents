"""Config regressions using OpenCode V1 `permission` rules (verified on 1.19.5).

OpenCode 1.x rejects the V2 `permissions` list in opencode.json and passes it
through as model options in agent frontmatter, so it would silently drop every
restriction. OpenCode 2.x still reads and normalizes the V1 map. These tests
model the rules; they do not run the shell scanner.
"""

import json
from pathlib import Path
import re
import unittest


REPO = Path(__file__).resolve().parents[1]
# OpenCode's native base policy, applied before global and agent-specific rules.
BASE_RULES = [
    {"action": "*", "resource": "*", "effect": "allow"},
    {"action": "doom_loop", "resource": "*", "effect": "ask"},
    {"action": "external_directory", "resource": "*", "effect": "ask"},
    {"action": "read", "resource": "*", "effect": "allow"},
    {"action": "read", "resource": "*.env", "effect": "ask"},
    {"action": "read", "resource": "*.env.*", "effect": "ask"},
    {"action": "read", "resource": "*.env.example", "effect": "allow"},
]
EFFECTS = ("allow", "deny", "ask")


def flatten(permission):
    """Expand a V1 `permission` map into ordered rules, as OpenCode does."""
    rules = []
    for action, value in permission.items():
        patterns = {"*": value} if isinstance(value, str) else value
        for resource, effect in patterns.items():
            rules.append({"action": action, "resource": resource, "effect": effect})
    return rules


def frontmatter_permission(text):
    """Parse the simple `permission:` block used by the OpenCode templates."""
    header = text.split("---", 2)[1]
    lines = header.splitlines()
    start = lines.index("permission:")
    permission = {}
    for line in lines[start + 1:]:
        if not line.startswith("  "):
            break
        key, _, value = line.strip().partition(": ")
        permission[key] = value
    return header, permission


def matches(pattern, value):
    patterns = (pattern, pattern[:-2]) if pattern.endswith(" *") else (pattern,)
    return any(
        re.fullmatch(
            re.escape(candidate).replace(r"\*", ".*").replace(r"\?", "."),
            value, flags=re.DOTALL,
        ) is not None
        for candidate in patterns
    )


def decision(rules, action, resource):
    effect = "ask"
    for rule in rules:
        if matches(rule["action"], action) and matches(rule["resource"], resource):
            effect = rule["effect"]
    return effect


class OpenCodeSecurityTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((REPO / "source/opencode.json").read_text())
        self.global_rules = flatten(self.config["permission"])
        self.rules = BASE_RULES + self.global_rules

    def test_config_uses_v1_permission_map_and_sharing_disabled(self):
        self.assertEqual(self.config["share"], "disabled")
        self.assertNotIn("permissions", self.config)
        for rule in self.global_rules:
            self.assertIn(rule["effect"], EFFECTS)
            # V2-only action names are not recognized by OpenCode 1.x.
            self.assertNotIn(rule["action"], ("shell", "subagent"))

    def test_read_only_agents_deny_edits_and_shell(self):
        templates = [REPO / "templates/defaults/opencode/agent.md",
                     *sorted((REPO / "templates/opencode/agents").glob("*.md"))]
        for path in templates:
            with self.subTest(template=path.name):
                header, permission = frontmatter_permission(path.read_text())
                self.assertNotIn("\npermissions:", header)
                self.assertEqual(permission["edit"], "deny")
                self.assertEqual(permission["bash"], "deny")
                rules = BASE_RULES + self.global_rules + flatten(permission)
                self.assertEqual(decision(rules, "edit", "src/app.py"), "deny")
                self.assertEqual(decision(rules, "bash", "git push"), "deny")
                self.assertEqual(decision(rules, "read", "src/app.py"), "allow")

    def test_routine_coding_and_file_reads_do_not_require_approval(self):
        for action, resource in (
            ("read", ".env"), ("read", "app/.env.local"), ("read", "secrets.json"),
            ("read", "certs/server.key"), ("read", ".env.example"),
            ("edit", "src/app.py"), ("grep", "timeout"), ("glob", "**/*.py"),
            ("bash", "git diff --cached"), ("bash", "git add src/app.py"),
            ("bash", "git commit -m fix"), ("bash", "python3 -m unittest"),
            ("bash", "npm run build"), ("task", "explore"), ("webfetch", "*"),
        ):
            with self.subTest(action=action, resource=resource):
                self.assertEqual(decision(self.rules, action, resource), "allow")

    def test_external_access_and_common_push_commands_ask(self):
        self.assertEqual(decision(self.rules, "external_directory", "/other/*"), "ask")
        for command in (
            "git push", "git push origin main", "git push --force-with-lease",
            "git -C repo push origin main", "git -c push.default=current push",
        ):
            with self.subTest(command=command):
                self.assertEqual(decision(self.rules, "bash", command), "ask")

    def test_global_rules_preserve_native_plan_and_general_restrictions(self):
        plan_defaults = [
            {"action": "edit", "resource": "*", "effect": "deny"},
            {"action": "edit", "resource": "/home/test/.opencode/plan/*", "effect": "allow"},
        ]
        general_defaults = [
            {"action": "question", "resource": "*", "effect": "deny"},
            {"action": "task", "resource": "*", "effect": "deny"},
        ]
        plan = BASE_RULES + plan_defaults + self.global_rules
        general = BASE_RULES + general_defaults + self.global_rules
        self.assertEqual(decision(plan, "edit", "src/app.py"), "deny")
        self.assertEqual(decision(plan, "edit", "/home/test/.opencode/plan/task.md"), "allow")
        self.assertEqual(decision(general, "task", "general"), "deny")
        self.assertEqual(decision(general, "question", "*"), "deny")


if __name__ == "__main__":
    unittest.main()
