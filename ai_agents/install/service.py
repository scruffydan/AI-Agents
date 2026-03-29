from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ai_agents.build.service import build_project
from ai_agents.domain.harnesses import HarnessSpec, select_harnesses
from ai_agents.domain.options import BuildOptions, InstallOptions
from ai_agents.fs import replace_file, replace_tree, resolve_relative_to


Prompt = Callable[[str], str]


@dataclass(frozen=True)
class InstallReport:
    build_dir: Path
    harnesses: tuple[HarnessSpec, ...]
    installed_targets: tuple[str, ...]


def install_project(options: InstallOptions, prompt: Prompt = input) -> InstallReport:
    repo_root = options.repo_root.resolve()
    build_dir = options.build_dir.resolve() if options.build_dir else repo_root / "build"
    harnesses = select_harnesses(options.selected_harnesses, include_all=False)
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


def install_harness(harness: HarnessSpec, build_dir: Path, home_dir: Path, force: bool, prompt: Prompt) -> list[str]:
    installed: list[str] = []
    build_root = build_dir / harness.output_layout.root

    for entry in harness.install_entries_for():
        source = resolve_relative_to(build_root, entry.source, f"install source for {harness.name}")
        destination = home_dir / entry.destination
        if entry.kind == "tree":
            installed.extend(install_tree(source, destination, force, prompt, label=entry.label))
            continue
        installed.extend(install_file(source, destination, force, prompt, label=entry.label))
    return installed


def install_tree(source: Path, destination: Path, force: bool, prompt: Prompt, label: str) -> list[str]:
    if not source.exists():
        return []
    if not should_write(destination, force, prompt, label=label):
        return []
    replace_tree(source, destination)
    return [str(destination)]


def install_file(source: Path, destination: Path, force: bool, prompt: Prompt, label: str) -> list[str]:
    if not source.exists():
        return []
    if not should_write(destination, force, prompt, label=label):
        return []
    replace_file(source, destination)
    return [str(destination)]


def should_write(path: Path, force: bool, prompt: Prompt, label: str | None = None) -> bool:
    if path.is_symlink():
        raise ValueError(f"refusing to overwrite symlink target: {path}")
    if force or not path.exists():
        return True
    target = label or str(path)
    answer = prompt(f"Overwrite {target}? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}
