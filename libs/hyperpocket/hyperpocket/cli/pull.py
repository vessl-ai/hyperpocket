import pathlib
from typing import Optional

import click

import hyperpocket.repository as repository


@click.command()
@click.argument("url", type=str)
@click.option("--lockfile", envvar="PATHS", type=click.Path(exists=True))
@click.option("--git-ref", type=str, default="HEAD")
def pull(url: str, lockfile: Optional[pathlib.Path], git_ref: str):
    if not lockfile:
        lockfile = pathlib.Path.cwd() / "pocket.lock"
    if not lockfile.exists():
        lockfile.touch()
    repository.pull(repository.Lockfile(path=lockfile), url, git_ref)
