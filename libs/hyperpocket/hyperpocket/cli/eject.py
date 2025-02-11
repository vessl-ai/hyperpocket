import pathlib
from typing import Optional

import click

import hyperpocket.repository as repository


@click.command()
@click.argument("url", type=str)
@click.argument("ref", type=str)
@click.argument("remote_path", type=str)
def eject(url: str, ref: str, remote_path: str):
    repository.eject(url, ref, remote_path)
