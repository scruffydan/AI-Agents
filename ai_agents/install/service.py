from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ai_agents.build.service import build_project
from ai_agents.domain.harnesses import HarnessSpec, select_harnesses
from ai_agents.domain.install_plan import InstallAction, InstallPlan
from ai_agents.domain.options import BuildOptions, InstallOptions
from ai_agents.fs import replace_file, replace_tree, resolve_relative_to


Prompt = Callable[[str], str]


@dataclass(frozen=True)
class InstallReport:
    build_dir: Path
    harnesses: tuple[HarnessSpec, ...]
    plan: InstallPlan
    installed_targets: tuple[str, ...]
    dry_run: bool


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

    plan = build_install_plan(harnesses, build_dir, home_dir, options.selected_components)
    installed = execute_install_plan(plan, force=options.force, prompt=prompt) if not options.dry_run else ()

    return InstallReport(
        build_dir=build_dir,
        harnesses=harnesses,
        plan=plan,
        installed_targets=installed,
        dry_run=options.dry_run,
    )


def build_install_plan(
    harnesses: tuple[HarnessSpec, ...],
    build_dir: Path,
    home_dir: Path,
    selected_components: tuple[str, ...],
) -> InstallPlan:
    actions: list[InstallAction] = []
    for harness in harnesses:
        build_root = build_dir / harness.output_layout.root
        for entry in harness.install_entries_for(selected_components):
            source = resolve_relative_to(build_root, entry.source, f"install source for {harness.name}")
            destination = home_dir / entry.destination
            status = "ready" if source.exists() else "missing_source"
            actions.append(
                InstallAction(
                    harness=harness.name,
                    component=entry.component,
                    label=entry.label,
                    source=source,
                    destination=destination,
                    kind=entry.kind,
                    status=status,
                )
            )
    return InstallPlan(build_dir=build_dir, actions=tuple(actions))


def execute_install_plan(plan: InstallPlan, force: bool, prompt: Prompt) -> tuple[str, ...]:
    installed: list[str] = []
    for action in plan.actions:
        if action.status != "ready":
            continue
        if not should_write(action.destination, force, prompt, label=action.label):
            continue
        if action.kind == "tree":
            replace_tree(action.source, action.destination)
        elif action.kind == "file":
            replace_file(action.source, action.destination)
        else:
            raise ValueError(f"unknown install action kind {action.kind!r}")
        installed.append(str(action.destination))
    return tuple(installed)


def should_write(path: Path, force: bool, prompt: Prompt, label: str | None = None) -> bool:
    if path.is_symlink():
        raise ValueError(f"refusing to overwrite symlink target: {path}")
    if force or not path.exists():
        return True
    target = label or str(path)
    answer = prompt(f"Overwrite {target}? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}
