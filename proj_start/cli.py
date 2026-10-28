"""Interactive implementation of the ``proj start`` command."""

from __future__ import annotations

import contextlib
import logging
import sys
from pathlib import Path

import click
from proj_conf.cli import install_shell_hook

from .model import ProjectMetadata
from .storage import (shell_exports, write_default_config, write_env_file,
                      write_loader_script)

LOGGER = logging.getLogger("proj")


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(("DEBUG", "INFO", "WARNING", "ERROR"), case_sensitive=False),
    default="INFO",
    show_default=True,
)
@click.option(
    "--print-export",
    is_flag=True,
    help="Print shell export commands after writing the metadata file.",
)
def start(log_level: str, print_export: bool) -> None:
    """Collect project metadata and write its .env file."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(levelname)s: %(message)s",
    )
    try:
        if print_export:
            # Keep stdout valid shell input; interactive prompts and status go to stderr.
            with contextlib.redirect_stdout(sys.stderr):
                metadata = collect_metadata()
                destination = write_env_file(metadata)
                loader = write_loader_script(metadata)
                write_default_config(metadata)
                install_shell_hook(loader)
        else:
            metadata = collect_metadata()
            destination = write_env_file(metadata)
    except (OSError, ValueError) as error:
        LOGGER.error("%s", error)
        raise click.ClickException(str(error)) from error

    if print_export:
        click.echo(shell_exports(metadata))
    else:
        click.echo(f"Project metadata written to {destination}")


def collect_metadata() -> ProjectMetadata:
    root = _directory_prompt("1. Enter the root directory of your project.")
    subprojects = _multi_prompt(
        "2. List nested project locations, one per line. Leave blank when finished."
    )
    languages = _multi_prompt(
        "3. List programming languages used, one per line. Leave blank when finished."
    )
    environment = click.prompt(
        "4. Enter the environment (filesystem, venv:/path, or container:/path)",
        default="filesystem",
    ).strip()
    if not environment:
        raise click.BadParameter("The project environment cannot be empty.")
    version = click.prompt("5. What is the most recent version of the project?").strip()
    if not version:
        raise click.BadParameter("The project version cannot be empty.")
    source = _directory_prompt("6. Enter the source folder location.")
    tests = _multi_prompt(
        "7. List test directory locations, one per line. Leave blank when finished."
    )
    git_directory = _directory_prompt("8. Enter the location of the project's .git folder.")
    ignored = _multi_prompt(
        "9. List locations to ignore, one per line. Leave blank when finished."
    )

    _ensure_inside(root, source, "source folder")
    _ensure_inside(root, git_directory, "git directory")
    return ProjectMetadata(
        root=root,
        subprojects=subprojects,
        languages=languages,
        environment=environment,
        version=version,
        source=source,
        tests=tests,
        git_directory=git_directory,
        ignored=ignored,
    )


def _directory_prompt(message: str) -> Path:
    value = click.prompt(message, type=click.Path(path_type=Path, file_okay=False))
    path = value.expanduser().resolve()
    if not path.is_dir():
        raise click.BadParameter(f"Directory does not exist: {path}")
    return path


def _multi_prompt(message: str) -> tuple[str, ...]:
    values: list[str] = []
    click.echo(message)
    while True:
        value = click.prompt("Location or value", default="", show_default=False).strip()
        if not value:
            return tuple(values)
        values.append(value)


def _ensure_inside(root: Path, child: Path, label: str) -> None:
    try:
        child.relative_to(root)
    except ValueError as error:
        raise click.BadParameter(f"The {label} must be inside the project root.") from error
