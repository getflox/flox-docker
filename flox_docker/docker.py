import click


@click.group()
@click.pass_obj
def docker(flox):
    """Manage SSM parameters"""
