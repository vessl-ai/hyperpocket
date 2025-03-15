import click


@click.command()
@click.argument("url", type=str)
@click.option("--git-ref", type=str, default="HEAD")
def pull(url: str, git_ref: str):
    pass