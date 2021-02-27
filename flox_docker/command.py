import click
from docker.errors import APIError, DockerException
from floxcore.console import success
from floxcore.context import Flox, EmptyContext
from floxcore.shell import execute_command

from flox_docker.client import docker_client


@click.group(name="docker", add_help_option=False, invoke_without_command=True, context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('--native', is_flag=True, default=False, help="Force usage of native command rather than flox wrapper")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
def docker_cli(flox: Flox, native, args):
    REIMPLEMENTED = dict(
        login=docker_login,
        run=docker_run
    )
    command_name = next(iter(args), None)

    if not native and command_name in REIMPLEMENTED.keys():
        cmd = REIMPLEMENTED.get(command_name)
        args = list(args)
        with EmptyContext(flox, cmd, args[1:], allow_interspersed_args=True, ignore_unknown_options=True) as ctx:
            return cmd.invoke(ctx)

    variables = flox.plugins.get("aws").handle("execution_context", flox)

    return execute_command("docker", args, variables)


@docker_cli.command(name="login")
@click.argument("repository")
@click.pass_obj
def docker_login(flox: Flox, repository: str):
    credentials = None
    for plugin in flox.plugins.handlers("docker_credentials").values():
        credentials = plugin.handle("docker_credentials", flox=flox, repository=repository)
        if credentials:
            break

    if not credentials:
        raise DockerException(f"Unable to locate credentials provider for repository {repository}")

    try:
        docker_client.login(username=credentials[0], password=credentials[1], registry=credentials[2])
        success(f"Logged in to {repository}")
    except APIError as e:
        raise DockerException(f"Failed to login: {e.explanation}")


@docker_cli.command(name="run", add_help_option=False)
@click.option("--with-security-from", multiple=True, help="Explicitly list allowed security contexts")
@click.option("--mount-project", default="/src", help="Mount current project root dir to given location")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
def docker_run(flox: Flox, with_security_from, mount_project, args):
    """Run docker container"""
    context = flox.security_context(with_security_from)
    args = list(args)
    args.insert(0, "run")

    for k, v in reversed({k: v for k, v in context.items() if v}.items()):
        args.insert(1, "-e")
        args.insert(2, f"{k}={v}")

    if mount_project:
        args.insert(1, "-v")
        args.insert(2, f"{flox.working_dir}:{mount_project}")

    execute_command("docker", args, context)
