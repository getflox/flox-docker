from click import Group
from floxcore.config import Configuration
from floxcore.context import Flox
from floxcore.plugin import Plugin

from flox_docker.command import docker_cli


class DockerConfiguration(Configuration):
    def parameters(self):
        return tuple()

    def schema(self):
        pass


class DockerPlugin(Plugin):
    def configuration(self):
        return DockerConfiguration()

    def handle_workflow_start(self, flox: Flox, **kwargs):
        return tuple()

    def add_commands(self, cli: Group):
        cli.add_command(docker_cli)


def plugin():
    return DockerPlugin()
