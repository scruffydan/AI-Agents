#!/usr/bin/env python3
"""AI-Agents build system - generates configs for multiple agent harnesses.

Usage:
    ./build.py                              # Build all (interactive)
    ./build.py claude opencode              # Build specific harnesses
    ./build.py --install                    # Build and install (interactive)
    ./build.py --install --yes              # Install without prompts
    ./build.py --work                       # Use work model mappings
    ./build.py --chatgpt-provider opencode  # Set GPT provider
    ./build.py --opus-provider github-copilot  # Set Opus provider

Requires Python 3.11+ (uses tomllib from stdlib).
"""

import argparse
import json
import re
import shutil
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).parent
SOURCE = REPO / "source"
BUILD = REPO / "build"

# ANSI colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"

# Valid providers per model family
PROVIDERS = {
    "gpt": ["openai", "opencode", "github-copilot"],
    "opus": ["opencode", "github-copilot"],
}


@dataclass
class ProviderConfig:
    """Per-model-family provider overrides.

    When --work mode is active, these are ignored and model-mappings.json is used instead.
    """

    gpt: str = "openai"  # --chatgpt-provider
    opus: str = "opencode"  # --opus-provider

    def rewrite_model(self, model: str) -> str:
        """Rewrite model string to use configured provider for its family."""
        if not model:
            return model

        # GPT models: */gpt-*
        if "/gpt-" in model:
            model_name = model.split("/", 1)[1]
            return f"{self.gpt}/{model_name}"

        # Opus models: */claude-opus*
        if "/claude-opus" in model:
            model_name = model.split("/", 1)[1]
            return f"{self.opus}/{model_name}"

        return model


# Harness configurations - add new harnesses here (e.g., codex)
HARNESSES = {
    "claude": {
        "agents_dir": "agents",
        "commands_dir": "commands",
        "skills_dir": "skills",
        "base_file": "CLAUDE.md",
        "install_path": Path.home() / ".claude",
    },
    "opencode": {
        "agents_dir": "agent",
        "commands_dir": "command",
        "skills_dir": "skill",
        "base_file": "AGENTS.md",
        "install_path": Path.home() / ".config" / "opencode",
    },
    # Example: Adding Codex support would be just:
    # "codex": {
    #     "agents_dir": "agents",
    #     "commands_dir": "commands",
    #     "skills_dir": "skills",
    #     "base_file": "CODEX.md",
    #     "install_path": Path.home() / ".codex",
    # },
}


def select_chatgpt_provider(model: str, provider: str) -> str:
    """Rewrite GPT model prefixes to use specified provider."""
    if not model:
        return model
    for prefix in ["openai/gpt-", "opencode/gpt-", "github-copilot/gpt-"]:
        if model.startswith(prefix):
            return f"{provider}/{model.split('/', 1)[1]}"
    return model


def parse_prompt(
    path: Path,
    model_map: dict | None = None,
    providers: ProviderConfig | None = None,
) -> tuple[dict, str]:
    """Parse TOML frontmatter (+++ delimited) and content from a prompt file."""
    text = path.read_text()
    parts = text.split("+++", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {path} (expected +++ delimiters)")

    _, frontmatter, content = parts
    config = tomllib.loads(frontmatter)

    # Process {{include:filename}} directives
    def include(m: re.Match) -> str:
        include_path = SOURCE / "prompts" / m.group(1)
        if not include_path.exists():
            print(f"{RED}Warning: Include file not found: {include_path}{NC}")
            return m.group(0)
        return include_path.read_text()

    content = re.sub(r"\{\{include:(.+?)\}\}", include, content)

    # Apply model transformations (provider rewrite first, then work mappings)
    if oc := config.get("opencode", {}):
        if model := oc.get("model"):
            if providers and not model_map:
                model = providers.rewrite_model(model)
            if model_map:
                model = model_map.get(model, model)
            oc["model"] = model

    return config, content.strip()


def to_yaml(data: dict, indent: int = 0) -> str:
    """Simple YAML serializer for output files (avoids pyyaml dependency)."""
    lines = []
    prefix = "  " * indent
    for key, val in data.items():
        if isinstance(val, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(to_yaml(val, indent + 1))
        elif isinstance(val, bool):
            lines.append(f"{prefix}{key}: {str(val).lower()}")
        elif isinstance(val, (int, float)):
            lines.append(f"{prefix}{key}: {val}")
        else:
            lines.append(f"{prefix}{key}: {val}")
    return "\n".join(lines)


def emit_file(harness: str, category: str, name: str, config: dict, content: str):
    """Generate output file for a specific harness."""
    h = HARNESSES[harness]
    out_dir = BUILD / harness / h[f"{category}s_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build harness-specific frontmatter
    fm: dict = {"description": config["description"]}

    if harness == "claude":
        if category == "agent":
            fm["name"] = name
        if c := config.get("claude"):
            for k in ["tools", "model"]:
                if v := c.get(k):
                    fm[k] = v
    else:  # opencode (and future harnesses can follow this pattern)
        if oc := config.get("opencode"):
            for k in [
                "mode",
                "model",
                "subtask",
                "temperature",
                "top_p",
                "frequency_penalty",
                "presence_penalty",
                "reasoningEffort",
            ]:
                if (v := oc.get(k)) is not None:
                    fm[k] = v
            if perm := oc.get("permission"):
                fm["permission"] = perm

    # Write file
    output_path = out_dir / f"{name}.md"
    output_path.write_text(f"---\n{to_yaml(fm)}\n---\n\n{content}\n")
    print(f"  {YELLOW}Created:{NC} {harness}/{h[f'{category}s_dir']}/{name}.md")


def build(
    harness_names: list[str],
    model_map: dict | None = None,
    providers: ProviderConfig | None = None,
    install: bool = False,
    include_config: bool = False,
    auto_yes: bool = False,
):
    """Build configs for specified harnesses."""
    print(f"{GREEN}Building AI-Agents configs...{NC}")
    print(f"Source: {SOURCE}")
    print(f"Output: {BUILD}")
    print(f"Harnesses: {', '.join(harness_names)}")
    if providers:
        print(f"Providers: gpt={providers.gpt}, opus={providers.opus}")
    print()

    # Clean build directory
    if BUILD.exists():
        shutil.rmtree(BUILD)

    # Process prompts
    prompts_dir = SOURCE / "prompts"
    for prompt in sorted(prompts_dir.glob("*.md")):
        # Skip partials and base instructions
        if prompt.name.startswith("_") or prompt.name == "AGENTS.md":
            continue

        print(f"{YELLOW}Processing:{NC} {prompt.name}")
        config, content = parse_prompt(prompt, model_map, providers)
        name = prompt.stem
        ptype = config["type"]

        for harness in harness_names:
            # Modes are OpenCode-only
            if ptype == "mode" and harness == "claude":
                continue
            category = "agent" if ptype in ("subagent", "mode") else "command"
            emit_file(harness, category, name, config, content)
        print()

    # Copy base instructions
    print(f"{YELLOW}Copying base instructions...{NC}")
    for harness in harness_names:
        h = HARNESSES[harness]
        dst_dir = BUILD / harness
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(prompts_dir / "AGENTS.md", dst_dir / h["base_file"])
        print(f"  {YELLOW}Created:{NC} {harness}/{h['base_file']}")
    print()

    # Copy skills
    skills_src = SOURCE / "skills"
    if skills_src.exists():
        print(f"{YELLOW}Copying skills...{NC}")
        for harness in harness_names:
            h = HARNESSES[harness]
            skills_dst = BUILD / harness / h["skills_dir"]
            shutil.copytree(skills_src, skills_dst)
            skill_count = len(list(skills_dst.iterdir()))
            print(
                f"  {YELLOW}Created:{NC} {harness}/{h['skills_dir']}/ ({skill_count} skills)"
            )
        print()

    # Copy opencode.json for OpenCode harness (only with --init-config flag)
    opencode_json = SOURCE / "opencode.json"
    if include_config and opencode_json.exists() and "opencode" in harness_names:
        print(f"{YELLOW}Copying OpenCode config...{NC}")
        shutil.copy(opencode_json, BUILD / "opencode" / "opencode.json")
        print(f"  {YELLOW}Created:{NC} opencode/opencode.json")
        print()

    # Summary
    print(f"{GREEN}{'=' * 60}{NC}")
    print(f"{GREEN}Build complete!{NC}")
    print(f"{GREEN}{'=' * 60}{NC}")
    print()

    for harness in harness_names:
        file_count = len(list((BUILD / harness).rglob("*.md")))
        print(f"  {harness}: {file_count} files")
    print()

    # Install if requested
    if install:
        print(f"{YELLOW}Installing...{NC}")
        for harness in harness_names:
            dest = HARNESSES[harness]["install_path"]
            src = BUILD / harness

            # Check for existing installation
            if dest.exists() and not auto_yes:
                print(f"  {YELLOW}Destination exists:{NC} {dest}")
                try:
                    choice = input("  Overwrite? [y/N]: ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n  Skipping...")
                    continue
                if choice not in ("y", "yes"):
                    print("  Skipping...")
                    continue

            shutil.copytree(src, dest, dirs_exist_ok=True)
            print(f"  {GREEN}Installed:{NC} {harness} -> {dest}")
        print()
        print(f"{GREEN}Installation complete!{NC}")
    else:
        print("Next step: Run ./build.py --install to install configs")


def prompt_choice(prompt: str, options: list[str], default: int = 0) -> str:
    """Interactive menu selection. Returns selected option."""
    print(f"{YELLOW}{prompt}{NC}")
    for i, opt in enumerate(options, 1):
        marker = " (default)" if i == default + 1 else ""
        print(f"  {i}) {opt}{marker}")
    print()
    try:
        choice = input(f"Choice [1-{len(options)}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return options[default]
    if not choice:
        return options[default]
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
    except ValueError:
        pass
    return options[default]


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "harnesses",
        nargs="*",
        default=[],
        choices=list(HARNESSES.keys()) + [[]],
        help="Harnesses to build (default: prompt or all)",
    )
    parser.add_argument(
        "--install", "-i", action="store_true", help="Install configs after building"
    )
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompts"
    )
    parser.add_argument(
        "--work", action="store_true", help="Use work environment model mappings"
    )
    parser.add_argument(
        "--chatgpt-provider",
        choices=PROVIDERS["gpt"],
        help="Provider for GPT models (openai, opencode, github-copilot)",
    )
    parser.add_argument(
        "--opus-provider",
        choices=PROVIDERS["opus"],
        help="Provider for Claude Opus models (opencode, github-copilot)",
    )
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="Include opencode.json (permission defaults) - usually only needed once",
    )
    args = parser.parse_args()

    interactive = sys.stdin.isatty() and not args.yes

    # Interactive harness selection if none specified
    if not args.harnesses:
        if interactive and args.install:
            choice = prompt_choice(
                "Select what to install:",
                ["Both (claude + opencode)", "OpenCode only", "Claude only"],
            )
            if "OpenCode" in choice and "claude" not in choice.lower():
                args.harnesses = ["opencode"]
            elif "Claude" in choice and "opencode" not in choice.lower():
                args.harnesses = ["claude"]
            else:
                args.harnesses = list(HARNESSES.keys())
            print()
        else:
            args.harnesses = list(HARNESSES.keys())

    # Build provider config from CLI args
    provider_config = ProviderConfig()
    if args.chatgpt_provider:
        provider_config.gpt = args.chatgpt_provider
    if args.opus_provider:
        provider_config.opus = args.opus_provider

    # Interactive provider selection for OpenCode (only if no CLI args provided)
    if (
        interactive
        and args.install
        and "opencode" in args.harnesses
        and not args.work
        and not args.chatgpt_provider
    ):
        provider_config.gpt = prompt_choice(
            "Select provider for GPT models:",
            PROVIDERS["gpt"],
        )
        print()

    # Load model mappings if --work specified
    model_map = None
    if args.work:
        mappings_file = SOURCE / "model-mappings.json"
        if mappings_file.exists():
            data = json.loads(mappings_file.read_text())
            model_map = data.get("models", {})
            print(f"{YELLOW}Using work model mappings from {mappings_file}{NC}")
            print()

    build(
        args.harnesses,
        model_map,
        provider_config if not args.work else None,
        args.install,
        args.init_config,
        args.yes,
    )


if __name__ == "__main__":
    main()
