"""Native agent formats and the few settings that differ by harness."""

import json
import re
import tomllib


def yaml_string(value: str) -> str:
    """Quote Unicode without JSON surrogate pairs or YAML line normalization."""
    quoted = json.dumps(value, ensure_ascii=False)
    return re.sub(r"[\x7f-\x9f\u2028\u2029]", lambda m: f"\\u{ord(m[0]):04x}", quoted)


def yaml_scalar(value: str) -> str:
    # Keep ordinary descriptions and model IDs readable, quoting YAML syntax.
    if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_./@-]*#[A-Za-z0-9_-]+", value):
        return value
    if (re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ .,/()@\"'?!-]*", value)
            and value == value.strip()
            and value.lower() not in {"null", "true", "false", "yes", "no", "on", "off"}):
        return value
    return yaml_string(value)


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False).replace("\x7f", "\\u007f")


def render_codex(agent: dict, model: str) -> str:
    body = agent["body"].replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    body = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", lambda m: f"\\u{ord(m[0]):04x}", body)
    effort = "low" if agent["name"] in {"docs-fetcher", "git-commit"} else "high"
    rendered = (
        f'name = {toml_string(agent["name"])}\n'
        f'description = {toml_string(agent["description"])}\n'
        f'model = {toml_string(model)}\n'
        f'model_reasoning_effort = "{effort}"\n'
        f'developer_instructions = """\n{body}\n"""\n'
    )
    if agent["name"] == "brainstorm":
        rendered += (
            '\n[features]\n'
            '# Keep the shell available for read-only repository inspection within the\n'
            '# inherited sandbox and approval policy.\n'
            'shell_tool = true\n'
        )
    tomllib.loads(rendered)
    return rendered


def render_claude(agent: dict, model: str) -> str:
    tools = {
        "docs-fetcher": "WebSearch, WebFetch",
        "git-commit": "Bash, Read, Grep, Glob",
    }.get(agent["name"], "Read, Glob, Grep")
    effort = "" if agent["name"] in {"docs-fetcher", "git-commit"} else "effort: high\n"
    return (
        f'---\nname: {yaml_scalar(agent["name"])}\n'
        f'description: {yaml_scalar(agent["description"])}\n'
        f'tools: {tools}\nmodel: {yaml_scalar(model)}\n{effort}'
        f'---\n\n{agent["body"]}\n'
    )


def render_opencode(agent: dict, model: str | None) -> str:
    name = agent["name"]
    primary = name == "brainstorm"
    description, body = agent["description"], agent["body"]
    if name == "brainstorm":
        description = (
            "Read-only idea generation on the configured brainstorm model. "
            "Select it when you want to brainstorm interactively."
        )
        body += (
            "\n\n## Working with the User\n\n"
            "You are talking with the user directly. Ask clarifying questions when the\n"
            "problem space is unclear, and offer to dive deeper into specific directions.\n"
            "For implementation, suggest switching to build mode; for concrete step-by-step\n"
            "plans, suggest plan mode."
        )

    rules = [("edit", "*", "deny"), ("shell", "*", "ask")]
    if name == "git-commit":
        # Exact commands preserve the existing allowance without permitting
        # write flags, redirects, external diff helpers, or text conversion.
        commands = (
            "git log",
            "git log -10 --format=full",
            "git log -10 --oneline --no-decorate",
            "git status",
            "git status --short",
            "git diff --no-ext-diff --no-textconv",
            "git diff --no-ext-diff --no-textconv --cached",
            "git diff --no-ext-diff --no-textconv --staged",
            "git show --no-ext-diff --no-textconv HEAD --stat",
        )
        rules.extend(("shell", command, "allow") for command in commands)
    if not primary:
        rules.extend((("question", "*", "deny"), ("subagent", "*", "deny")))
    permissions = "".join(
        f'  - action: {action}\n    resource: {yaml_string(resource)}\n    effect: {effect}\n'
        for action, resource, effect in rules
    )
    model_line = f"model: {yaml_scalar(model)}\n" if model is not None else ""
    return (
        f'---\ndescription: {yaml_scalar(description)}\n'
        f'mode: {"primary" if primary else "subagent"}\n{model_line}'
        f'permissions:\n{permissions}---\n\n{body}\n'
    )


RENDERERS = {"codex": render_codex, "claude": render_claude, "opencode": render_opencode}
