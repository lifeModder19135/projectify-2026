"""Read and validate the project configuration file."""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

VALID_SCOPES = {"when in project", "always", "never"}


@dataclass(frozen=True)
class ProjectConfig:
    env_scope: str
    entry_hooks: tuple[str, ...]
    change_hooks: tuple[str, ...]


def read_config(path: Path) -> ProjectConfig:
    parser = configparser.ConfigParser(interpolation=None, delimiters=("="), strict=True)
    if not path.is_file():
        raise ValueError(f"Configuration file does not exist: {path}")
    parser.read(path, encoding="utf-8")
    if not parser.has_section("project"):
        raise ValueError("Configuration must contain a [project] section")

    section = parser["project"]
    scope = section.get("env-scope", "").strip()
    if scope not in VALID_SCOPES:
        raise ValueError(
            "env-scope must be one of: when in project, always, never"
        )
    return ProjectConfig(
        env_scope=scope,
        entry_hooks=_list_value(section.get("project-entry-hooks", "")),
        change_hooks=_list_value(section.get("project-change-hooks", "")),
    )


def _list_value(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(":") if item.strip())
