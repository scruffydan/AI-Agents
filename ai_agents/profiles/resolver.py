from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from ai_agents.domain.models import ResolvedModelConfig


ProfileData = dict[str, Any]


def load_model_profiles(path: Path) -> dict[str, ProfileData]:
    data = tomllib.loads(path.read_text())
    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError(f"{path} must define a [profiles] table")
    return profiles


def resolve_model_profile(
    profiles: dict[str, ProfileData],
    profile_name: str,
    environment: str,
    harness: str,
) -> ResolvedModelConfig:
    try:
        environments = profiles[profile_name]
    except KeyError as exc:
        known = ", ".join(sorted(profiles))
        raise ValueError(f"unknown model profile {profile_name!r}; expected one of: {known}") from exc

    shared_values = get_profile_shared_settings(profile_name, environments)

    try:
        environment_values = environments[environment]
    except KeyError as exc:
        raise ValueError(
            f"missing profile entry for profile={profile_name!r}, "
            f"environment={environment!r}, harness={harness!r}"
        ) from exc

    if not isinstance(environment_values, dict):
        raise ValueError(f"profile={profile_name!r}, environment={environment!r} must be a table")

    try:
        harness_values = environment_values[harness]
    except KeyError as exc:
        raise ValueError(
            f"missing profile entry for profile={profile_name!r}, "
            f"environment={environment!r}, harness={harness!r}"
        ) from exc

    if not isinstance(harness_values, dict):
        raise ValueError(
            f"profile={profile_name!r}, environment={environment!r}, harness={harness!r} must be a table"
        )

    model = harness_values.get("model")
    if not isinstance(model, str) or not model:
        raise ValueError(
            f"profile={profile_name!r}, environment={environment!r}, harness={harness!r} "
            "must define a non-empty model"
        )

    settings = dict(shared_values)
    settings.update({key: value for key, value in harness_values.items() if key != "model"})
    return ResolvedModelConfig(
        profile_name=profile_name,
        environment=environment,
        harness=harness,
        model=model,
        settings=settings,
    )


def get_profile_shared_settings(profile_name: str, profile: ProfileData) -> dict[str, Any]:
    shared_values = profile.get("shared", {})
    if not isinstance(shared_values, dict):
        raise ValueError(f"profile={profile_name!r} shared settings must be a table")
    return dict(shared_values)
