#!/usr/bin/env python3
"""Report adapted upstream files that changed after their pinned commit.

Pins are read from the GitHub links already in README.md, THIRD_PARTY_NOTICES.md,
and source/, so there is no separate list to maintain. Content is compared by blob
SHA, because some pins are commits that did not touch the linked file.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")

ROOT = Path(__file__).resolve().parent
API = "https://api.github.com"
PIN = re.compile(
    r"https://github\.com/([\w.-]+)/([\w.-]+)/blob/([0-9a-f]{40})/([^\s)#?`>\]]+)"
)

Pin = tuple[str, str, str, str]  # owner, repo, sha, path


def find_pins(root: Path) -> dict[Pin, list[str]]:
    """Map each pinned upstream file to the repository files that cite it."""
    files = [root / "README.md", root / "THIRD_PARTY_NOTICES.md"]
    files += sorted((root / "source").rglob("*.md"))
    pins: dict[Pin, list[str]] = defaultdict(list)
    for file in files:
        if not file.is_file():
            continue
        cited_in = file.relative_to(root).as_posix()
        for match in PIN.finditer(file.read_text(encoding="utf-8")):
            if cited_in not in pins[match.groups()]:
                pins[match.groups()].append(cited_in)
    return dict(pins)


def conflicting_pins(pins: dict[Pin, list[str]]) -> list[str]:
    """Describe upstream files pinned to more than one commit."""
    shas: dict[tuple[str, str, str], list[Pin]] = defaultdict(list)
    for pin in pins:
        owner, repo, _, path = pin
        shas[(owner, repo, path)].append(pin)
    problems = []
    for (owner, repo, path), group in sorted(shas.items()):
        if len(group) > 1:
            cited = "; ".join(f"`{p[2][:7]}` in {', '.join(pins[p])}" for p in sorted(group))
            problems.append(f"{owner}/{repo}: {path} has different pins: {cited}")
    return problems


def get(url: str):
    """GET a GitHub API URL and return the decoded JSON, or None on 404."""
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def check(pin: Pin, branches: dict[tuple[str, str], str]) -> tuple[str, list[str]]:
    """Return a status (same, changed, missing, broken) and report lines."""
    owner, repo, sha, path = pin
    base = f"{API}/repos/{owner}/{repo}"
    if (owner, repo) not in branches:
        info = get(base)
        if info is None:
            return "broken", [f"Repository {owner}/{repo} was not found."]
        branches[(owner, repo)] = info["default_branch"]
    branch = branches[(owner, repo)]

    quoted = urllib.parse.quote(path)
    pinned = get(f"{base}/contents/{quoted}?ref={sha}")
    if pinned is None:
        return "broken", ["No file at this path in the pinned commit; fix the link."]
    current = get(f"{base}/contents/{quoted}?ref={urllib.parse.quote(branch)}")
    if current is None:
        return "missing", [f"Moved or deleted upstream: no file at this path on `{branch}`."]
    if pinned["sha"] == current["sha"]:
        return "same", []

    # The commit list only explains the change; the blob comparison above decides it.
    since = get(f"{base}/commits/{sha}")["commit"]["committer"]["date"]
    query = urllib.parse.urlencode({"path": path, "sha": branch, "since": since, "per_page": 100})
    commits = [c for c in get(f"{base}/commits?{query}") if c["sha"] != sha]
    lines = [f"Changed upstream ({len(commits)} commit(s) on this path since the pin):"]
    for commit in commits:
        date = commit["commit"]["committer"]["date"][:10]
        subject = commit["commit"]["message"].splitlines()[0]
        lines.append(f"- `{commit['sha'][:7]}` {date} {subject}")
    if commits:
        lines.append(f"Candidate new pin: `{commits[0]['sha']}`")
    lines += [
        "Review:",
        "```sh",
        f'git clone --filter=blob:none --no-checkout https://github.com/{owner}/{repo}.git "$TMPDIR/{repo}"',
        f'git -C "$TMPDIR/{repo}" diff {sha} origin/{branch} -- {path}',
        "```",
    ]
    return "changed", lines


def ordered(pins: dict[Pin, list[str]]) -> list[tuple[Pin, list[str]]]:
    """Sort by upstream repository and path so related files sit together."""
    return sorted(pins.items(), key=lambda item: (item[0][0].lower(), item[0][1], item[0][3]))


def heading(pin: Pin, cited_in: list[str]) -> list[str]:
    owner, repo, sha, path = pin
    return [f"## {owner}/{repo}: {path}", f"Pinned `{sha[:7]}` in: {', '.join(cited_in)}"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--list", action="store_true", help="list pinned files without contacting GitHub"
    )
    parser.add_argument("--report", type=Path, help="also write the Markdown report to this file")
    args = parser.parse_args(argv)

    pins = find_pins(ROOT)
    problems = conflicting_pins(pins)
    if args.list:
        for pin, cited_in in ordered(pins):
            print("\n".join(heading(pin, cited_in)) + "\n")
        for problem in problems:
            print(f"Error: {problem}", file=sys.stderr)
        return 2 if problems else 0

    sections = [f"## Inconsistent pins\n{problem}" for problem in problems]
    status_code = 2 if problems else 0
    branches: dict[tuple[str, str], str] = {}
    for pin, cited_in in ordered(pins):
        status, lines = check(pin, branches)
        if status != "same":
            status_code = max(status_code, 2 if status == "broken" else 1)
            sections.append("\n".join(heading(pin, cited_in) + lines))

    report = "\n\n".join(sections) or f"All {len(pins)} pinned upstream files match their pins."
    print(report)
    if args.report:
        args.report.write_text(report + "\n", encoding="utf-8")
    return status_code


if __name__ == "__main__":
    raise SystemExit(main())
