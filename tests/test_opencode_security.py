"""Configuration regressions against documented V2 matching, not a shell sandbox test."""

import json
from pathlib import Path
import re
import unittest


REPO = Path(__file__).resolve().parents[1]


def matches(pattern, value):
    # V2 supports only whole-value * and ? wildcards, not fnmatch's [] syntax.
    expression = re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")
    return re.fullmatch(expression, value, flags=re.DOTALL) is not None or (
        pattern.endswith(" *") and value == pattern[:-2]
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
        self.rules = self.config["permissions"]

    def test_config_keeps_v2_rules_and_sharing_disabled(self):
        self.assertEqual(self.config["share"], "disabled")
        self.assertNotIn("permission", self.config)
        for rule in self.rules:
            self.assertEqual(set(rule), {"action", "resource", "effect"})
            self.assertIn(rule["effect"], ("allow", "deny", "ask"))
            self.assertNotIn(rule["action"], ("bash", "task", "doom_loop", "lsp"))

    def test_sensitive_reads_are_denied_at_root_nested_and_absolute_paths(self):
        names = (
            ".env", ".env.local", ".env.example.local", "secrets.json",
            "secrets.production.json", "prod-secrets.yaml", "prod-secrets.yml",
            "server.key", "server.pem", "id_ed25519", ".ssh/config",
            ".aws/config", ".gcloud/config", ".config/gcloud/access_tokens.db",
            ".docker/config.json", ".kube/config", ".gnupg/private-keys-v1.d/key",
            ".npmrc", ".pypirc", ".netrc", ".pgpass", ".git-credentials",
            "service-account-prod.json", "application_default_credentials.json",
            "terraform.tfvars", "prod.tfvars.json", "terraform.tfstate.backup",
            "terraform.tfstate", "custom.tfstate", "opencode/auth.json",
            ".ssh/.env.example", ".aws/.env.example",
        )
        for prefix in ("", "packages/app/", "/home/test/project/"):
            for name in names:
                with self.subTest(path=prefix + name):
                    self.assertEqual(decision(self.rules, "read", prefix + name), "deny")

    def test_environment_examples_and_public_certificates_remain_readable(self):
        for path in (
            ".env.example", "app/.env.example", "/home/test/project/.env.example",
            "README.md", "src/app.py", "certs/public.crt", "id_ed25519.pub",
        ):
            with self.subTest(path=path):
                self.assertEqual(decision(self.rules, "read", path), "allow")

    def test_exact_inspection_commands_are_allowed(self):
        for command in (
            "pwd", "ls", "ls -la", "git status", "git status --short",
            "git status --short --branch", "git diff --stat",
            "git diff --cached --stat", "git log --oneline -10",
        ):
            with self.subTest(command=command):
                self.assertEqual(decision(self.rules, "shell", command), "allow")

    def test_mutations_arbitrary_flags_and_prefix_lookalikes_ask(self):
        for command in (
            "git branch -D main", "git add .", "git commit -am message", "git push",
            "git status-custom", "git diff --ext-diff", "git log --output=tracked.txt",
            "git show HEAD:.env", "git -c core.fsmonitor=helper status",
            "ls /home/test/.ssh", "lsof", "echo private", "which helper",
            "fd --exec helper", "curl https://example.com", "npm install",
            "rm -rf build", "/bin/rm file", "find . -delete", "python3 script.py",
        ):
            with self.subTest(command=command):
                self.assertEqual(decision(self.rules, "shell", command), "ask")
        # Compound-command parsing belongs to OpenCode's scanner, not this matcher.

    def test_unlisted_actions_content_search_and_external_access_ask(self):
        for action, resource in (
            ("edit", "src/app.py"), ("grep", "password"),
            ("external_directory", "/home/test/other/*"), ("subagent", "general"),
            ("execute", "*"), ("new_mcp_tool", "*"),
        ):
            with self.subTest(action=action):
                self.assertEqual(decision(self.rules, action, resource), "ask")

    def test_global_defaults_do_not_weaken_built_in_plan_and_general_limits(self):
        plan = self.rules + self.config["agents"]["plan"]["permissions"]
        for action, resource in (
            ("edit", "src/app.py"), ("edit", "/home/test/.opencode/plan/plan.md"),
            ("shell", "git status"), ("subagent", "general"),
        ):
            with self.subTest(action=action, resource=resource):
                self.assertEqual(decision(plan, action, resource), "deny")
        general = self.rules + self.config["agents"]["general"]["permissions"]
        self.assertEqual(decision(general, "subagent", "general"), "deny")
        self.assertEqual(decision(general, "question", "*"), "deny")


if __name__ == "__main__":
    unittest.main()
