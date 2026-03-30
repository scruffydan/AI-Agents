from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from ai_agents.build.service import build_project
from ai_agents.content.loader import load_validated_documents
from ai_agents.content.validation import lint_shared_content
from ai_agents.doctor import render_doctor_report, run_doctor
from ai_agents.domain.harnesses import OutputComponent, all_harnesses, select_harnesses
from ai_agents.domain.options import BuildOptions, InstallOptions
from ai_agents.install.service import install_project
from ai_agents.repo import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__))
OPENCODE_PROVIDERS = ("openai", "github-copilot", "opencode")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-agents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Plan or run a build")
    build_parser.add_argument(
        "--harness",
        action="append",
        dest="harnesses",
        default=[],
        help="Harness to target. Repeatable.",
    )
    build_parser.add_argument(
        "--all",
        action="store_true",
        help="Build every registered harness.",
    )
    build_parser.add_argument(
        "--work",
        action="store_true",
        help="Use the work environment model profiles.",
    )
    build_parser.add_argument(
        "--output",
        type=Path,
        help="Output directory. Defaults to <repo>/build.",
    )
    build_parser.add_argument(
        "--opencode-provider",
        choices=OPENCODE_PROVIDERS,
        help="Override the OpenCode provider for this build.",
    )

    list_parser = subparsers.add_parser("list", help="List project metadata")
    list_subparsers = list_parser.add_subparsers(dest="list_command", required=True)
    list_subparsers.add_parser("harnesses", help="List registered harnesses")

    install_parser = subparsers.add_parser("install", help="Install generated artifacts")
    install_parser.add_argument(
        "--harness",
        action="append",
        dest="harnesses",
        default=[],
        help="Harness to install. Repeatable.",
    )
    install_parser.add_argument("--all", action="store_true", help="Install all harnesses")
    install_parser.add_argument("--work", action="store_true", help="Use work environment")
    install_parser.add_argument("--skip-build", action="store_true", help="Use existing build output")
    install_parser.add_argument("--force", action="store_true", help="Overwrite without prompts")
    install_parser.add_argument("--dry-run", action="store_true", help="Show planned install actions without writing files")
    install_parser.add_argument(
        "--opencode-provider",
        choices=OPENCODE_PROVIDERS,
        help="Override the OpenCode provider for the build performed by install.",
    )
    install_parser.add_argument(
        "--component",
        action="append",
        dest="components",
        default=[],
        choices=("base", "documents", "skills"),
        help="Install only selected components. Repeatable.",
    )

    doctor_parser = subparsers.add_parser("doctor", help="Verify source, build, and installed state")
    doctor_parser.add_argument("--installed", action="store_true", help="Verify installed targets under the home directory")
    doctor_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    subparsers.add_parser("lint", help="Validate source content and harness neutrality")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build":
        return handle_build(args)
    if args.command == "list" and args.list_command == "harnesses":
        return handle_list_harnesses()
    if args.command == "install":
        return handle_install(args)
    if args.command == "doctor":
        return handle_doctor(args)
    if args.command == "lint":
        return handle_lint()

    parser.error("unknown command")
    return 2


def handle_build(args: argparse.Namespace) -> int:
    selected = select_harnesses(args.harnesses, include_all=args.all)
    options = BuildOptions(
        repo_root=REPO_ROOT,
        output_dir=args.output,
        selected_harnesses=tuple(spec.name for spec in selected),
        environment="work" if args.work else "default",
        opencode_provider_override=args.opencode_provider,
    )
    report = build_project(options)

    print(f"Repo root: {report.repo_root}")
    print(f"Output dir: {report.output_dir}")
    print(f"Environment: {report.environment}")
    if args.opencode_provider:
        print(f"OpenCode provider override: {args.opencode_provider}")
    print(f"Harnesses: {', '.join(spec.name for spec in report.harnesses)}")
    print(f"Documents: {report.document_count}")
    print(f"Artifacts: {report.artifact_count}")
    print(f"Skills copied: {report.skill_count}")
    print(f"Base files: {report.base_file_count}")
    return 0


def handle_list_harnesses() -> int:
    for spec in all_harnesses():
        kinds = ",".join(kind.value for kind in spec.supported_kinds)
        default_flag = "yes" if spec.default_selected else "no"
        print(f"{spec.name}: default={default_flag} base={spec.base_filename} kinds={kinds}")
    return 0


def handle_install(args: argparse.Namespace) -> int:
    selected = select_harnesses(args.harnesses, include_all=args.all)
    components = normalize_components(args.components)
    report = install_project(
        InstallOptions(
            repo_root=REPO_ROOT,
            selected_harnesses=tuple(spec.name for spec in selected),
            selected_components=components,
            environment="work" if args.work else "default",
            opencode_provider_override=args.opencode_provider,
            skip_build=args.skip_build,
            force=args.force,
            dry_run=args.dry_run,
        )
    )
    print(f"Build dir: {report.build_dir}")
    if args.opencode_provider:
        print(f"OpenCode provider override: {args.opencode_provider}")
    print(f"Harnesses: {', '.join(spec.name for spec in report.harnesses)}")
    if components:
        print(f"Components: {', '.join(components)}")
    if report.dry_run:
        print(f"Planned actions: {len(report.plan.actions)}")
        return 0
    print(f"Installed targets: {len(report.installed_targets)}")
    return 0


def normalize_components(values: list[str]) -> tuple[OutputComponent, ...]:
    seen: set[str] = set()
    normalized: list[OutputComponent] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return tuple(normalized)


def handle_lint() -> int:
    prompts_dir = REPO_ROOT / "source" / "prompts"
    documents = load_validated_documents(prompts_dir, include_dir=prompts_dir)

    report = lint_shared_content(REPO_ROOT)
    if report.violations:
        for violation in report.violations:
            print(violation)
        return 1

    print(f"Checked files: {report.checked_files}")
    print(f"Documents: {len(documents)}")
    print("Lint passed")
    return 0


def handle_doctor(args: argparse.Namespace) -> int:
    report = run_doctor(REPO_ROOT, verify_installed=args.installed)
    if args.json:
        import json

        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render_doctor_report(report))
    return 0 if report.ok else 1
