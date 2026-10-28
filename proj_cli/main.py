"""The stable ``proj`` command and its subcommand registration."""

from __future__ import annotations

import click
from proj_conf.cli import conf
from proj_start.cli import start
from proj_watch.cli import watch


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(context: click.Context) -> None:
    """Manage project-specific environment metadata."""
    if context.invoked_subcommand is None:
        click.echo(context.get_help())


cli.add_command(start)
cli.add_command(conf)
cli.add_command(watch)

if __name__ == "__main__":
    cli()
