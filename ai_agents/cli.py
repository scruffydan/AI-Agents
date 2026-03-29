from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from ai_agents.build.service import build_project
from ai_agents.domain.harnesses import all_harnesses, select_harnesses
from ai_agents.domain.options import BuildOptions
from ai_agents.repo import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__))


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

    init_parser = subparsers.add_parser("init", help="Initialize harness-specific config")
    init_subparsers = init_parser.add_subparsers(dest="init_command", required=True)
    init_opencode = init_subparsers.add_parser("opencode", help="Initialize OpenCode config")
    init_opencode.add_argument("--force", action="store_true", help="Overwrite without prompts")

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
        print("install is not implemented yet; Phase 1 is focused on core architecture scaffolding.")
        return 2
    if args.command == "init" and args.init_command == "opencode":
        print("init opencode is not implemented yet; install safety work lands in a later phase.")
        return 2
    if args.command == "lint":
        print("lint is not implemented yet; source migration and harness-neutrality checks land next.")
        return 2

    parser.error("unknown command")
    return 2


def handle_build(args: argparse.Namespace) -> int:
    selected = select_harnesses(args.harnesses, all_harnesses=args.all)
    options = BuildOptions(
        repo_root=REPO_ROOT,
        output_dir=args.output,
        selected_harnesses=tuple(spec.name for spec in selected),
        environment="work" if args.work else "default",
    )
    report = build_project(options)

    print(f"Repo root: {report.repo_root}")
    print(f"Output dir: {report.output_dir}")
    print(f"Environment: {report.environment}")
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
        print(
            f"{spec.name}: default={default_flag} install={spec.install_target} "
            f"base={spec.base_filename} kinds={kinds}"
        )
    return 0
