import click

from hyperpocket.cli.eject import eject
from hyperpocket.cli.pull import pull
from hyperpocket.cli.sync import sync
from hyperpocket.cli.eject import eject
from hyperpocket.cli.auth_token import create_token_auth_template
from hyperpocket.cli.auth_oauth2 import create_oauth2_auth_template
from hyperpocket.cli.tool_create import create_tool_template, build_tool
from hyperpocket.cli.tool_export import export_tool


@click.group()
def cli():
    pass


@click.group()
def devtool():
    pass


cli.add_command(devtool)
devtool.add_command(create_token_auth_template)
devtool.add_command(create_oauth2_auth_template)
devtool.add_command(create_tool_template)
devtool.add_command(build_tool)
devtool.add_command(export_tool)

cli.add_command(pull)
cli.add_command(sync)
cli.add_command(eject)

cli()
