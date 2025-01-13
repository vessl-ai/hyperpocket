import click

from hyperpocket.cli.pull import pull
from hyperpocket.cli.sync import sync
from hyperpocket.cli.eject import eject
from hyperpocket.cli.auth import start_token_auth


@click.group()
def cli():
    pass

@click.group()
def auth():
    pass

cli.add_command(auth)
auth.add_command(start_token_auth)

cli.add_command(pull)
cli.add_command(sync)
cli.add_command(eject)

cli()
