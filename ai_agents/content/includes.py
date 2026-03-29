from __future__ import annotations

import re
from pathlib import Path


INCLUDE_PATTERN = re.compile(r"\{\{include:(.+?)\}\}")


def expand_includes(text: str, include_dir: Path, seen: tuple[Path, ...] = ()) -> str:
    def replace(match: re.Match[str]) -> str:
        include_name = match.group(1).strip()
        include_path = (include_dir / include_name).resolve()

        if include_path in seen:
            chain = " -> ".join(str(path) for path in (*seen, include_path))
            raise ValueError(f"include cycle detected: {chain}")
        if not include_path.exists():
            raise ValueError(f"include file not found: {include_path}")

        included = include_path.read_text()
        return expand_includes(included, include_dir, (*seen, include_path))

    return INCLUDE_PATTERN.sub(replace, text)
