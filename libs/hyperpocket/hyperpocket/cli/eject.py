import pathlib
from typing import Optional

import click

import hyperpocket.repository as repository


@click.command()
@click.argument("url", type=str)
@click.argument("ref", type=str)
@click.argument("remote_path", type=str)
@click.option("--lockfile", envvar="PATHS", type=click.Path(exists=True))
def eject(url: str, ref: str, remote_path: str, lockfile: Optional[pathlib.Path]):
    if not lockfile:
        lockfile = pathlib.Path.cwd() / "pocket.lock"
    if not lockfile.exists():
        raise ValueError("To eject a tool, you first need to pull it")
    repository.eject(url, ref, remote_path, repository.Lockfile(lockfile))
