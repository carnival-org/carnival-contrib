import os
import typing

from carnival import Connection
from carnival import Step
from carnival import cmd
from carnival.exceptions import StepValidationError
from carnival.templates import render

from carnival_contrib import systemd


class Deploy(Step):
    """
    Upload docker-compose service and related files.
    """
    def __init__(
            self,
            app_dir: str,

            template_files: typing.List[typing.Union[str, typing.Tuple[str, str]]],
            template_context: typing.Dict[str, typing.Any],

            scale: typing.Optional[typing.Dict[str, int]] = None,
            start_service: bool = True,
    ):
        """
        :param app_dir: Application remote destination directory
        :param template_files: List of templates to upload. Can be file name or tuple (source_file, dest_file_name)
        :param template_context: template files context
        :param scale: scale service when start. for example 'webapp=2 redis=2'
        :param start_service: start service after upload
        """
        self.app_dir = app_dir

        self.template_files: typing.List[typing.Tuple[str, str]] = []
        for dest in template_files:
            if isinstance(dest, str):
                source_file = dest
                dest_fname = os.path.basename(source_file)
            elif isinstance(dest, tuple):
                source_file, dest_fname = dest
            else:
                raise ValueError(f"Cant parse template_file definition: {dest}")

            self.template_files.append((source_file, dest_fname))

        self.template_context = template_context
        self.scale = scale
        self.start_service = start_service

    def validate(self, c: Connection) -> None:
        if not cmd.cli.is_cmd_exist(c, "docker"):
            raise StepValidationError("'docker' is required")

        if not cmd.cli.is_cmd_exist(c, "docker-compose"):
            raise StepValidationError("'docker-compose' is required")

        # Validate template rendering
        for source_file, _ in self.template_files:
            render(source_file, **self.template_context)

    def run(self, c: Connection) -> typing.Any:
        systemd.Start("docker").run(c=c)

        cmd.cli.run(c, f"mkdir -p {self.app_dir}")

        for source_file, dest_fname in self.template_files:
            cmd.transfer.put_template(
                c,
                source_file, os.path.join(self.app_dir, dest_fname),
                **self.template_context
            )

        cmd.cli.run(c, f"cd {self.app_dir}; docker-compose rm -f")

        if self.start_service:
            if self.scale:
                scale_str = " ".join([f" --scale {service_name}={count}" for service_name, count in self.scale.items()])
            else:
                scale_str = ""
            cmd.cli.run(c, f"cd {self.app_dir}; docker-compose up -d --remove-orphans {scale_str}")


class Ps(Step):
    """
    docker-compose ps
    """

    subcommand = "ps"

    def __init__(self, app_dir: str):
        """
        :param app_dir: Application remote directory
        """
        self.app_dir = app_dir

    def validate(self, c: "Connection") -> None:
        if not cmd.cli.is_cmd_exist(c, "docker-compose"):
            raise StepValidationError("'docker-compose' is required")

    def run(self, c: Connection) -> typing.Any:
        cmd.cli.run(c, f"cd {self.app_dir}; docker-compose {self.subcommand}")


class Restart(Ps):
    """
    docker-compose restart
    """

    subcommand = "restart"


class RestartServices(Step):
    """
    docker-compose restart [services...]
    """

    subcommand = "restart"

    def __init__(self, app_dir: str, services: typing.List[str]):
        """
        :param app_dir: Application remote directory
        """
        self.app_dir = app_dir
        self.services = " ".join(services)
        self.services = self.services.strip()

    def validate(self, c: "Connection") -> None:
        if not self.services:
            raise StepValidationError("'services' must not be empty")

        if not cmd.cli.is_cmd_exist(c, "docker-compose"):
            raise StepValidationError("'docker-compose' is required")

    def run(self, c: Connection) -> typing.Any:
        cmd.cli.run(c, f"cd {self.app_dir}; docker-compose {self.subcommand} {self.services}")


class Stop(Ps):
    """
    docker-compose stop
    """
    subcommand = "stop"


class StopServices(RestartServices):
    """
    docker-compose logs -f --tail=tail
    """
    subcommand = "stop"


class Logs(Step):
    """
    docker-compose restart [services...]
    """

    def __init__(self, app_dir: str, tail: int = 20):
        """
        :param app_dir: Application remote directory
        """
        self.app_dir = app_dir
        self.tail = tail

    def validate(self, c: "Connection") -> None:
        if not cmd.cli.is_cmd_exist(c, "docker-compose"):
            raise StepValidationError("'docker-compose' is required")

    def run(self, c: Connection) -> typing.Any:
        cmd.cli.run(c, f"cd {self.app_dir}; docker-compose logs -f --tail={self.tail}")


class LogsServices(Step):
    """
    docker-compose logs -f --tail=tail [services...]
    """

    def __init__(self, app_dir: str, services: typing.List[str], tail: int = 20):
        """
        :param app_dir: Application remote directory
        """
        self.app_dir = app_dir
        self.services = " ".join(services)
        self.services = self.services.strip()
        self.tail = tail

    def validate(self, c: "Connection") -> None:
        if not self.services:
            raise StepValidationError("'services' must not be empty")

        if not cmd.cli.is_cmd_exist(c, "docker-compose"):
            raise StepValidationError("'docker-compose' is required")

    def run(self, c: Connection) -> typing.Any:
        cmd.cli.run(c, f"cd {self.app_dir}; docker-compose logs -f --tail={self.tail} {self.services}")
