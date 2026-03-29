from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ai_agents.build.service import build_project
from ai_agents.domain.harnesses import HarnessSpec, select_harnesses
from ai_agents.domain.options import BuildOptions, InstallOptions
from ai_agents.fs import ensure_dir


Prompt = Callable[[str], str]


@dataclass(frozen=True)
class InstallReport:
    build_dir: Path
    harnesses: tuple[HarnessSpec, ...]
    installed_targets: tuple[str, ...]


def install_project(options: InstallOptions, prompt: Prompt = input) -> InstallReport:
    repo_root = options.repo_root.resolve()
    build_dir = options.build_dir.resolve() if options.build_dir else repo_root / "build"
    harnesses = select_harnesses(options.selected_harnesses, all_harnesses=False)
    home_dir = options.home_dir.resolve() if options.home_dir else Path.home()

    if not options.skip_build:
        build_project(
            BuildOptions(
                repo_root=repo_root,
                output_dir=build_dir,
                selected_harnesses=tuple(spec.name for spec in harnesses),
                environment=options.environment,
            )
        )

    installed: list[str] = []
    for harness in harnesses:
        installed.extend(install_harness(harness, build_dir, home_dir, options.force, prompt))

    return InstallReport(build_dir=build_dir, harnesses=harnesses, installed_targets=tuple(installed))


def init_opencode_config(repo_root: Path, force: bool = False, prompt: Prompt = input, home_dir: Path | None = None) -> Path | None:
    source = repo_root / "source" / "opencode.json"
    target_home = home_dir.resolve() if home_dir else Path.home()
    destination = target_home / ".config" / "opencode" / "opencode.json"
    if not source.exists():
        raise ValueError(f"missing source config: {source}")
    if not should_write(destination, force, prompt):
        return None
    ensure_dir(destination.parent)
    shutil.copy2(source, destination)
    return destination


def install_harness(harness: HarnessSpec, build_dir: Path, home_dir: Path, force: bool, prompt: Prompt) -> list[str]:
    if harness.name == "opencode":
        return install_tree(build_dir / "opencode", home_dir / ".config" / "opencode", force, prompt, label="opencode")
    if harness.name == "claude":
        return install_tree(build_dir / "claude", home_dir / ".claude", force, prompt, label="claude")
    if harness.name == "codex":
        return install_codex(build_dir / "codex", home_dir, force, prompt)
    raise ValueError(f"unknown harness {harness.name!r}")


def install_codex(build_root: Path, home_dir: Path, force: bool, prompt: Prompt) -> list[str]:
    installed: list[str] = []
    codex_home = home_dir / ".codex"
    agents_home = home_dir / ".agents" / "skills"

    installed.extend(install_tree(build_root / ".codex", codex_home, force, prompt, label="codex agents"))
    installed.extend(install_tree(build_root / ".agents" / "skills", agents_home, force, prompt, label="codex skills"))

    agents_file = build_root / "AGENTS.md"
    target_file = codex_home / "AGENTS.md"
    if should_write(target_file, force, prompt):
        ensure_dir(target_file.parent)
        shutil.copy2(agents_file, target_file)
        installed.append(str(target_file))
    return installed


def install_tree(source: Path, destination: Path, force: bool, prompt: Prompt, label: str) -> list[str]:
    if not source.exists():
        return []
    if not should_write(destination, force, prompt, label=label):
        return []
    ensure_dir(destination.parent)
    shutil.copytree(source, destination, dirs_exist_ok=True)
    return [str(destination)]


def should_write(path: Path, force: bool, prompt: Prompt, label: str | None = None) -> bool:
    if force or not path.exists():
        return True
    target = label or str(path)
    answer = prompt(f"Overwrite {target}? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}
