"""Polling watcher for project entry and file-change hooks."""

from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

import click
from proj_conf.cli import _find_project_root
from proj_conf.config import read_config

LOGGER = logging.getLogger("proj")


@click.command()
@click.option("--interval", type=click.FloatRange(min=0.1), default=1.0, show_default=True)
def watch(interval: float) -> None:
    """Run project hooks while watching the current project."""
    root = _find_project_root(Path.cwd())
    config_path = root / ".prj" / "config" / "conf"
    try:
        config = read_config(config_path)
    except ValueError as error:
        raise click.ClickException(str(error)) from error

    _run_hooks(config.entry_hooks, root)
    snapshot = _snapshot(root)
    click.echo(f"Watching {root}. Press Ctrl-C to stop.")
    try:
        while True:
            time.sleep(interval)
            current = _snapshot(root)
            if current != snapshot:
                _run_hooks(config.change_hooks, root)
                snapshot = current
    except KeyboardInterrupt:
        click.echo("\nStopped.")


def _snapshot(root: Path) -> dict[str, int]:
    ignored = {".git", ".prj", ".venv", "__pycache__"} 
    return {
        str(path.relative_to(root)): path.stat().st_mtime_ns
        for path in root.rglob("*")
        if path.is_file() and not any(part in ignored for part in path.relative_to(root).parts)
    }


def _run_hooks(hooks: tuple[str, ...], root: Path) -> None:
    for hook in hooks:
        LOGGER.info("Running project hook: %s", hook)
        subprocess.run(hook, shell=True, cwd=root, check=True)
