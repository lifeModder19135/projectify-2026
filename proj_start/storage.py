"""Persist project metadata in a shell-compatible, INI-valid file."""

from __future__ import annotations

import logging
from pathlib import Path

from .model import ProjectMetadata

LOGGER = logging.getLogger(__name__)


def choose_config_directory(root: Path, environment: str) -> Path:
    """Choose the requested environment config directory, then project config."""
    environment_path = _environment_path(environment)
    if environment_path is not None:
        candidate = environment_path / "config"
        if candidate.is_dir():
            return candidate

    for name in ("config", ".config"):
        candidate = root / name
        if candidate.is_dir():
            return candidate
    return root


def write_env_file(metadata: ProjectMetadata) -> Path:
    destination = metadata.project_directory / ".env"
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as output:
        for name, value in metadata.as_ini_values().items():
            output.write(f"export {name}={_shell_quote(value)}\n")
    LOGGER.info("Wrote project metadata to %s", destination)
    return destination


def write_loader_script(metadata: ProjectMetadata) -> Path:
    destination = metadata.project_directory / "load.sh"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
_PROJ_CONFIG_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
_PROJ_ROOT="$(cd -- "$_PROJ_CONFIG_DIR/../.." && pwd)"
_PROJ_SCOPE="when in project"
if [[ -f "$_PROJ_CONFIG_DIR/conf" ]]; then
    _PROJ_SCOPE="$(awk -F= '/^[[:space:]]*env-scope[[:space:]]*=/{gsub(/[[:space:]]/, "", $2); print $2}' "$_PROJ_CONFIG_DIR/conf")"
fi
case "$_PROJ_SCOPE" in
    always)
        source "$_PROJ_CONFIG_DIR/.env"
        ;;
    wheninproject)
        case "$PWD/" in "$_PROJ_ROOT/"*) source "$_PROJ_CONFIG_DIR/.env" ;; esac
        ;;
    never)
        ;;
    *)
        printf 'proj: invalid env-scope in %s/conf\n' "$_PROJ_CONFIG_DIR" >&2
        return 1 2>/dev/null || exit 1
        ;;
esac
unset _PROJ_CONFIG_DIR _PROJ_ROOT _PROJ_SCOPE
""",
        encoding="utf-8",
    )
    destination.chmod(0o755)
    LOGGER.info("Wrote project loader to %s", destination)
    return destination


def write_default_config(metadata: ProjectMetadata) -> Path:
    destination = metadata.project_directory / "conf"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        destination.write_text(
            "[project]\n"
            "env-scope = when in project\n"
            "project-entry-hooks =\n"
            "project-change-hooks =\n",
            encoding="utf-8",
        )
    return destination


def _environment_path(environment: str) -> Path | None:
    if not environment.startswith(("venv:", "container:")):
        return None
    _, raw_path = environment.split(":", maxsplit=1)
    return Path(raw_path).expanduser() if raw_path else None


def shell_exports(metadata: ProjectMetadata) -> str:
    """Return safely quoted exports suitable for ``eval`` or ``source`` use."""
    return "\n".join(
        f"export {name}={_shell_quote(value)}"
        for name, value in metadata.as_ini_values().items()
    )


def _shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"
