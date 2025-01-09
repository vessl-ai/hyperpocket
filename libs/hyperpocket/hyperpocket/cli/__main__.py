import click

from hyperpocket.cli.pull import pull
from hyperpocket.cli.sync import sync
from hyperpocket.cli.eject import eject


@click.group()
def cli():
    pass


cli.add_command(pull)
cli.add_command(sync)
cli.add_command(eject)

cli()
