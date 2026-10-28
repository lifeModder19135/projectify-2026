"""The ``proj conf`` command."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import click

from .config import read_config

LOGGER = logging.getLogger("proj")


@click.command(name="conf")
@click.option("--validate", "-v", is_flag=True, help="Validate without changing shell startup.")
def conf(validate: bool) -> None:
    """Validate or apply the project configuration in the current directory."""
    root = _find_project_root(Path.cwd())
    config_path = root / ".prj" / "config" / "conf"
    try:
        read_config(config_path)
        if not validate:
            install_shell_hook(root / ".prj" / "config" / "load.sh")
    except (OSError, ValueError) as error:
        raise click.ClickException(str(error)) from error
    click.echo("Configuration is valid." if validate else "Configuration applied.")


def _find_project_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".prj" / "config" / "conf").is_file():
            return candidate
    raise click.ClickException("No .prj/config/conf found in this directory or its parents.")


def install_shell_hook(loader: Path) -> None:
    shell = os.environ.get("SHELL", "")
    shell_name = Path(shell).name
    rc_name = {
        "bash": ".bashrc",
        "zsh": ".zshrc",
        "ksh": ".kshrc",
        "fish": "config.fish",
    }.get(shell_name)
    if rc_name is None:
        raise ValueError(f"Unsupported shell: {shell_name or 'unknown'}")
    rc_path = Path.home() / ".config" / "fish" / rc_name if shell_name == "fish" else Path.home() / rc_name
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    marker = f"# proj: load {loader}"
    existing = rc_path.read_text(encoding="utf-8") if rc_path.exists() else ""
    if marker not in existing:
        with rc_path.open("a", encoding="utf-8") as output:
            output.write(f"\n{marker}\nsource {shlex_quote(str(loader))}\n")


def shlex_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"
