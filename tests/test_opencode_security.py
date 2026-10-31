"""Config regressions using documented V2 rules; these do not run the shell scanner."""

import json
from pathlib import Path
import re
import unittest


REPO = Path(__file__).resolve().parents[1]
# OpenCode's native base policy, applied before global and agent-specific rules.
BASE_RULES = [
    {"action": "*", "resource": "*", "effect": "allow"},
    {"action": "read", "resource": "*.env", "effect": "ask"},
    {"action": "read", "resource": "*.env.*", "effect": "ask"},
    {"action": "read", "resource": "*.env.example", "effect": "allow"},
]


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
        self.rules = BASE_RULES + self.config["permissions"]

    def test_config_keeps_v2_rules_and_sharing_disabled(self):
        self.assertEqual(self.config["share"], "disabled")
        self.assertNotIn("permission", self.config)
        for rule in self.config["permissions"]:
            self.assertEqual(set(rule), {"action", "resource", "effect"})
            self.assertIn(rule["effect"], ("allow", "deny", "ask"))
            self.assertNotIn(rule["action"], ("bash", "task", "doom_loop", "lsp"))

    def test_routine_coding_and_file_reads_do_not_require_approval(self):
        for action, resource in (
            ("read", ".env"), ("read", "app/.env.local"), ("read", "secrets.json"),
            ("read", "certs/server.key"), ("read", ".env.example"),
            ("edit", "src/app.py"), ("grep", "timeout"), ("glob", "**/*.py"),
            ("shell", "git diff --cached"), ("shell", "git add src/app.py"),
            ("shell", "git commit -m fix"), ("shell", "python3 -m unittest"),
            ("shell", "npm run build"), ("subagent", "explore"), ("execute", "*"),
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
                self.assertEqual(decision(self.rules, "shell", command), "ask")

    def test_global_rules_preserve_native_plan_and_general_restrictions(self):
        plan_defaults = [
            {"action": "edit", "resource": "*", "effect": "deny"},
            {"action": "edit", "resource": "/home/test/.opencode/plan/*", "effect": "allow"},
        ]
        general_defaults = [
            {"action": "question", "resource": "*", "effect": "deny"},
            {"action": "subagent", "resource": "*", "effect": "deny"},
        ]
        plan = BASE_RULES + plan_defaults + self.config["permissions"]
        general = BASE_RULES + general_defaults + self.config["permissions"]
        self.assertEqual(decision(plan, "edit", "src/app.py"), "deny")
        self.assertEqual(decision(plan, "edit", "/home/test/.opencode/plan/task.md"), "allow")
        self.assertEqual(decision(general, "subagent", "general"), "deny")
        self.assertEqual(decision(general, "question", "*"), "deny")


if __name__ == "__main__":
    unittest.main()
