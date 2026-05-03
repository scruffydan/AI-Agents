from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ai_agents.content.loader import load_validated_documents
from ai_agents.domain.harnesses import all_harnesses, get_harness
from ai_agents.profiles.resolver import load_model_profiles


@dataclass(frozen=True)
class DoctorIssue:
    scope: str
    message: str


@dataclass
class DoctorReport:
    repo_root: str
    build_dir: str
    checked: list[str] = field(default_factory=list)
    warnings: list[DoctorIssue] = field(default_factory=list)
    failures: list[DoctorIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_root": self.repo_root,
            "build_dir": self.build_dir,
            "checked": self.checked,
            "warnings": [asdict(issue) for issue in self.warnings],
            "failures": [asdict(issue) for issue in self.failures],
            "ok": self.ok,
        }


def run_doctor(
    repo_root: Path,
    *,
    verify_installed: bool,
    home_dir: Path | None = None,
    build_dir: Path | None = None,
) -> DoctorReport:
    repo_root = repo_root.resolve()
    resolved_build_dir = build_dir.resolve() if build_dir else repo_root / "build"
    report = DoctorReport(repo_root=str(repo_root), build_dir=str(resolved_build_dir))

    check_source(repo_root, report)
    manifest = check_build(resolved_build_dir, report)
    if verify_installed:
        check_installed(home_dir.resolve() if home_dir else Path.home(), report, manifest)

    return report


def check_source(repo_root: Path, report: DoctorReport) -> None:
    prompts_dir = repo_root / "source" / "prompts"
    profiles_path = repo_root / "source" / "model-profiles.toml"
    report.checked.append("source")

    try:
        load_validated_documents(prompts_dir, include_dir=prompts_dir)
        load_model_profiles(profiles_path)
    except Exception as exc:
        report.failures.append(DoctorIssue(scope="source", message=str(exc)))
        return

    for harness in all_harnesses():
        if not harness.install_entries:
            report.failures.append(DoctorIssue(scope="source", message=f"harness {harness.name} has no install entries"))


def check_build(build_dir: Path, report: DoctorReport) -> dict[str, Any] | None:
    manifest_path = build_dir / "manifest.json"
    report.checked.append("build")

    if not manifest_path.exists():
        report.warnings.append(DoctorIssue(scope="build", message=f"build manifest not found: {manifest_path}"))
        return None

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        report.failures.append(DoctorIssue(scope="build", message=f"invalid manifest JSON: {exc}"))
        return None

    required_keys = {"schema_version", "repo_root", "output_dir", "environment", "harnesses", "documents", "artifacts"}
    missing = sorted(required_keys - set(manifest))
    if missing:
        report.failures.append(DoctorIssue(scope="build", message=f"manifest missing keys: {', '.join(missing)}"))
        return None

    seen_paths: set[str] = set()
    for artifact in manifest["artifacts"]:
        relative_output_path = artifact["relative_output_path"]
        if relative_output_path in seen_paths:
            report.failures.append(DoctorIssue(scope="build", message=f"duplicate artifact path in manifest: {relative_output_path}"))
            continue
        seen_paths.add(relative_output_path)

        artifact_path = build_dir / Path(relative_output_path)
        if not artifact_path.exists():
            report.failures.append(DoctorIssue(scope="build", message=f"manifest references missing artifact: {relative_output_path}"))
    return manifest


def check_installed(home_dir: Path, report: DoctorReport, manifest: dict[str, Any] | None) -> None:
    report.checked.append("installed")

    if manifest is None:
        report.failures.append(DoctorIssue(scope="installed", message="installed verification requires a build manifest"))
        return

    missing: list[str] = []
    installed_components = {
        (artifact["harness"], artifact["component"])
        for artifact in manifest.get("artifacts", [])
        if "harness" in artifact and "component" in artifact
    }
    for harness_name in manifest.get("harnesses", []):
        harness = get_harness(harness_name)
        for entry in harness.install_entries:
            if (harness.name, entry.component) not in installed_components:
                continue
            destination = home_dir / entry.destination
            if not destination.exists():
                missing.append(str(destination))

    if missing:
        preview = ", ".join(missing[:3])
        extra = len(missing) - min(len(missing), 3)
        suffix = f" (+{extra} more)" if extra else ""
        report.failures.append(DoctorIssue(scope="installed", message=f"missing installed targets: {preview}{suffix}"))


def render_doctor_report(report: DoctorReport) -> str:
    lines = [f"Repo root: {report.repo_root}", f"Build dir: {report.build_dir}", f"Checks: {', '.join(report.checked)}"]
    if report.warnings:
        lines.append(f"Warnings: {len(report.warnings)}")
        lines.extend(f"- [{issue.scope}] {issue.message}" for issue in report.warnings)
    if report.failures:
        lines.append(f"Failures: {len(report.failures)}")
        lines.extend(f"- [{issue.scope}] {issue.message}" for issue in report.failures)
    else:
        lines.append("Doctor passed")
    return "\n".join(lines)
