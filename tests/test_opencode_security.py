"""Config regressions using a local model of V2 permissions, not the OpenCode runtime."""

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
EFFECTS = ("allow", "deny", "ask")
ANALYSIS_TEMPLATES = [
    "templates/defaults/opencode/agent.md",
    "templates/opencode/agents/brainstorm.md",
    "templates/opencode/agents/thorough-plan.md",
]
READ_TEMPLATES = [
    *ANALYSIS_TEMPLATES,
    "templates/overrides/opencode/git-commit.md",
]
DOCS_TEMPLATE = "templates/overrides/opencode/docs-fetcher.md"


def frontmatter_permissions(text):
    """Parse the simple V2 rule lists used by the OpenCode templates."""
    header = text.split("---", 2)[1]
    rules = [
        {"action": json.loads(action) if action.startswith('"') else action,
         "resource": resource, "effect": effect}
        for action, resource, effect in re.findall(
            r'- action: (\S+)\n\s+resource: "([^"]*)"\n\s+effect: (\S+)', header
        )
    ]
    return header, rules


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
        self.global_rules = self.config["permissions"]
        self.rules = BASE_RULES + self.global_rules

    def agent_rules(self, template):
        _, agent_rules = frontmatter_permissions((REPO / template).read_text())
        self.assertTrue(agent_rules)
        return self.rules + agent_rules

    def test_config_keeps_v2_rules_and_sharing_disabled(self):
        self.assertEqual(self.config["share"], "disabled")
        self.assertNotIn("permission", self.config)
        for rule in self.global_rules:
            self.assertEqual(set(rule), {"action", "resource", "effect"})
            self.assertIn(rule["effect"], EFFECTS)
            self.assertNotIn(rule["action"], ("bash", "task", "doom_loop", "lsp"))

    def test_read_only_agents_deny_edits_and_ask_for_shell(self):
        templates = [REPO / "templates/defaults/opencode/agent.md",
                     *sorted((REPO / "templates/opencode/agents").glob("*.md"))]
        for path in templates:
            with self.subTest(template=path.name):
                header, agent_rules = frontmatter_permissions(path.read_text())
                self.assertNotIn("\npermission:", header)
                self.assertTrue(agent_rules)
                rules = self.rules + agent_rules
                self.assertEqual(decision(rules, "edit", "src/app.py"), "deny")
                for command in ("git diff --cached", "python3 -m unittest", "git push"):
                    with self.subTest(command=command):
                        self.assertEqual(decision(rules, "shell", command), "ask")
                self.assertEqual(decision(rules, "read", "src/app.py"), "allow")
                for action, resource in (("glob", "**/*.py"), ("grep", "timeout"),
                                         ("execute", "*")):
                    self.assertEqual(decision(rules, action, resource), "allow")
                self.assertEqual(
                    decision(rules, "external_directory", "/other/*"), "ask"
                )
                if path == templates[0]:
                    self.assertEqual(decision(rules, "question", "*"), "deny")

    def test_global_and_agent_rules_preserve_native_env_prompts(self):
        policies = [("global", self.rules)]
        for template in READ_TEMPLATES:
            policies.append((template, self.agent_rules(template)))
        for policy, rules in policies:
            for resource, effect in (
                (".env", "ask"), (".env.local", "ask"),
                ("app/.env", "ask"), ("app/.env.local", "ask"),
                ("src/app.py", "allow"), (".env.example", "allow"),
                ("app/.env.example", "allow"),
            ):
                with self.subTest(policy=policy, resource=resource):
                    self.assertEqual(decision(rules, "read", resource), effect)

    def test_custom_agents_deny_unapproved_tools_and_mcp_actions(self):
        for template in [*READ_TEMPLATES, DOCS_TEMPLATE]:
            rules = self.agent_rules(template)
            for action, resource in (
                ("edit", "src/app.py"), ("future_tool", "*"),
                ("github_create_issue", "*"), ("documents_update_page", "*"),
                ("documentation_read_page", "*"),
                ("opencode_list_mcp_resources", "documentation"),
                ("opencode_read_mcp_resource", "documentation:docs://api"),
            ):
                with self.subTest(template=template, action=action):
                    self.assertEqual(decision(rules, action, resource), "deny")

    def test_only_documentation_delegation_is_approved_for_analysis_agents(self):
        for template in [*READ_TEMPLATES, DOCS_TEMPLATE]:
            rules = self.agent_rules(template)
            expected_docs = "allow" if template in ANALYSIS_TEMPLATES else "deny"
            with self.subTest(template=template):
                self.assertEqual(decision(rules, "subagent", "docs-fetcher"), expected_docs)
                for child in ("general", "explore", "code-security", "docs-fetcher-extra"):
                    self.assertEqual(decision(rules, "subagent", child), "deny")

    def test_only_interactive_primaries_can_ask_questions(self):
        for template in [*READ_TEMPLATES, DOCS_TEMPLATE]:
            expected = "allow" if template.startswith("templates/opencode/agents/") else "deny"
            with self.subTest(template=template):
                self.assertEqual(decision(self.agent_rules(template), "question", "*"), expected)

    def test_only_thorough_plan_can_load_its_required_skill(self):
        for template in [*READ_TEMPLATES, DOCS_TEMPLATE]:
            rules = self.agent_rules(template)
            expected = "allow" if template.endswith("/thorough-plan.md") else "deny"
            with self.subTest(template=template):
                self.assertEqual(decision(rules, "skill", "mode-thorough-plan"), expected)
                self.assertEqual(decision(rules, "skill", "git-push"), "deny")

    def test_docs_fetcher_has_web_access_without_local_tools_or_delegation(self):
        rules = self.agent_rules(DOCS_TEMPLATE)
        for action, resource in (("websearch", "OpenCode V2 permissions"),
                                 ("webfetch", "https://opencode.ai/v2/docs/permissions/"),
                                 ("execute", "*")):
            with self.subTest(action=action):
                self.assertEqual(decision(rules, action, resource), "allow")
        for action, resource in (("read", "src/app.py"), ("read", ".env"),
                                 ("glob", "**/*.py"), ("grep", "timeout"),
                                 ("shell", "git status"),
                                 ("external_directory", "/other/*")):
            with self.subTest(action=action):
                self.assertEqual(decision(rules, action, resource), "deny")
        for template in READ_TEMPLATES:
            for action, resource in (("websearch", "OpenCode V2 permissions"),
                                     ("webfetch", "https://opencode.ai/v2/docs/permissions/")):
                with self.subTest(template=template, action=action):
                    self.assertEqual(decision(self.agent_rules(template), action, resource), "deny")

    def test_routine_coding_and_file_reads_do_not_require_approval(self):
        for action, resource in (
            ("read", "src/app.py"), ("read", "secrets.json"),
            ("read", "certs/server.key"), ("read", ".env.example"),
            ("edit", "src/app.py"), ("grep", "timeout"), ("glob", "**/*.py"),
            ("shell", "git diff --cached"), ("shell", "git add src/app.py"),
            ("shell", "git commit -m fix"), ("shell", "python3 -m unittest"),
            ("shell", "npm run build"), ("subagent", "explore"),
            ("webfetch", "https://example.com/docs"), ("execute", "*"),
        ):
            with self.subTest(action=action, resource=resource):
                self.assertEqual(decision(self.rules, action, resource), "allow")

    def test_external_access_requires_approval(self):
        self.assertEqual(decision(self.rules, "external_directory", "/other/*"), "ask")

    def test_global_config_leaves_push_commands_at_native_default(self):
        for command in (
            "git push", "git push origin main", "git push --force-with-lease",
            "git -C repo push origin main", "git -c push.default=current push",
        ):
            with self.subTest(command=command):
                self.assertEqual(decision(self.rules, "shell", command), "allow")

    def test_global_rules_preserve_native_plan_and_general_restrictions(self):
        plan_defaults = [
            {"action": "edit", "resource": "*", "effect": "deny"},
            {"action": "edit", "resource": "/home/test/.opencode/plan/*", "effect": "allow"},
        ]
        general_defaults = [
            {"action": "question", "resource": "*", "effect": "deny"},
            {"action": "subagent", "resource": "*", "effect": "deny"},
        ]
        plan = BASE_RULES + plan_defaults + self.global_rules
        general = BASE_RULES + general_defaults + self.global_rules
        self.assertEqual(decision(plan, "edit", "src/app.py"), "deny")
        self.assertEqual(decision(plan, "edit", "/home/test/.opencode/plan/task.md"), "allow")
        self.assertEqual(decision(general, "subagent", "general"), "deny")
        self.assertEqual(decision(general, "question", "*"), "deny")

    def test_git_commit_agent_only_runs_read_only_git(self):
        header, agent_rules = frontmatter_permissions(
            (REPO / "templates/overrides/opencode/git-commit.md").read_text()
        )
        self.assertNotIn("\npermission:", header)
        self.assertTrue(agent_rules)
        rules = self.rules + agent_rules
        for command in (
            "git log", "git log -10 --oneline --no-decorate",
            "git status", "git status --short",
            "git diff --no-ext-diff --no-textconv",
            "git diff --no-ext-diff --no-textconv --cached",
            "git diff --no-ext-diff --no-textconv --staged",
            "git show --no-ext-diff --no-textconv HEAD --stat",
        ):
            with self.subTest(command=command):
                self.assertEqual(decision(rules, "shell", command), "allow")
        for command in (
            "git add src/app.py", "git commit -m fix", "git push",
            "git -C repo push origin log", "rm -rf build", "python3 -m unittest",
            "git -C repo add log README.md", "git -C repo reset --hard log HEAD",
            "git -C repo log -5", "git -C repo diff --staged",
            "git log -1 --output=README.md", "git diff --output=README.md",
            "git show HEAD --output README.md",
            "git diff --no-ext-diff --no-textconv --output=README.md",
            "git log -10 --oneline --no-decorate --output=README.md",
            "git diff --ext-diff", "git diff --textconv", "git diff", "git show",
        ):
            with self.subTest(command=command):
                self.assertEqual(decision(rules, "shell", command), "ask")
        for resource in ("src/app.py", "README.md"):
            self.assertEqual(decision(rules, "edit", resource), "deny")
        self.assertEqual(decision(rules, "question", "*"), "deny")


if __name__ == "__main__":
    unittest.main()
