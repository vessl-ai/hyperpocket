import pathlib
from typing import Optional

import click

import hyperpocket.repository as repository


@click.command()
@click.argument("url", type=str)
@click.option("--git-ref", type=str, default="HEAD")
def pull(url: str, git_ref: str):
    repository.pull(url, git_ref)
