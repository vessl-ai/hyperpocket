import pathlib
from typing import Optional

import click

import hyperpocket.repository as repository


@click.command()
@click.option("--lockfile", envvar="PATHS", type=click.Path(exists=True))
@click.option("--force-update", type=str, default="HEAD")
def sync(lockfile: Optional[pathlib.Path], force_update: bool):
    if not lockfile:
        lockfile = pathlib.Path.cwd() / "pocket.lock"
    if not lockfile.exists():
        lockfile.touch()
    repository.sync(repository.Lockfile(path=lockfile), force_update)
