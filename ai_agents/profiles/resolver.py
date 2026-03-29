from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from ai_agents.domain.models import ResolvedModelConfig


ProfileData = dict[str, Any]
PROVIDER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


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

    settings = dict(shared_values)
    if harness == "opencode":
        model = resolve_opencode_model(profile_name, environment, harness_values)
        settings.update({key: value for key, value in harness_values.items() if key not in {"provider", "model"}})
    else:
        if "provider" in harness_values:
            raise ValueError(
                f"profile={profile_name!r}, environment={environment!r}, harness={harness!r} "
                "does not support provider"
            )
        model = require_model_name(profile_name, environment, harness, harness_values)
        settings.update({key: value for key, value in harness_values.items() if key != "model"})

    return ResolvedModelConfig(
        model=model,
        settings=settings,
    )


def get_profile_shared_settings(profile_name: str, profile: ProfileData) -> dict[str, Any]:
    shared_values = profile.get("shared", {})
    if not isinstance(shared_values, dict):
        raise ValueError(f"profile={profile_name!r} shared settings must be a table")
    return dict(shared_values)


def resolve_opencode_model(profile_name: str, environment: str, values: dict[str, Any]) -> str:
    provider = values.get("provider")
    if not isinstance(provider, str) or not provider:
        raise ValueError(
            f"profile={profile_name!r}, environment={environment!r}, harness='opencode' "
            "must define a non-empty provider"
        )
    if not PROVIDER_PATTERN.match(provider):
        raise ValueError(
            f"profile={profile_name!r}, environment={environment!r}, harness='opencode' "
            f"has invalid provider {provider!r}"
        )

    model_name = require_model_name(profile_name, environment, "opencode", values)
    if "/" in model_name:
        raise ValueError(
            f"profile={profile_name!r}, environment={environment!r}, harness='opencode' "
            "must use split provider/model fields"
        )

    return compose_opencode_model(provider, model_name)


def require_model_name(profile_name: str, environment: str, harness: str, values: dict[str, Any]) -> str:
    model_name = values.get("model")
    if not isinstance(model_name, str) or not model_name:
        raise ValueError(
            f"profile={profile_name!r}, environment={environment!r}, harness={harness!r} "
            "must define a non-empty model"
        )
    return model_name


def compose_opencode_model(provider: str, model_name: str) -> str:
    return f"{provider}/{model_name}"
