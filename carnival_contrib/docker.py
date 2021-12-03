import os
import typing

from carnival import Step
from carnival import cmd
from carnival import Connection
from carnival.steps import validators

from carnival_contrib import apt, systemd


class CeInstallUbuntu(Step):
    def __init__(self, docker_version: typing.Optional[str] = None) -> None:
        """
        Install docker-ce on ubuntu

        :param docker_version: docker-ce version to install
        """
        self.docker_version = docker_version

    def get_validators(self) -> typing.List[validators.StepValidatorBase]:
        return [
            validators.CommandRequiredValidator("apt-get"),
            validators.CommandRequiredValidator("curl"),
        ]

    def run(self, c: Connection) -> bool:
        """
        :return: True if installed, False if was already installed
        """
        # https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/

        pkgname = "docker-ce"
        if apt.IsPackageInstalled(pkgname=pkgname, version=self.docker_version).run(c=c):
            print(f"{pkgname} already installed")
            return False

        print(f"Installing {pkgname}...")
        cmd.cli.run(c, "sudo apt-get update")
        cmd.cli.run(c, "sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common")
        cmd.cli.run(c, "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -")
        cmd.cli.run(c, 'sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')

        apt.ForceInstall(pkgname=pkgname, version=self.docker_version, update=True, hide=True).run(c=c)
        return True


class ComposeInstall(Step):
    def __init__(
        self,
        docker_compose_version: str = "1.25.1",
        docker_compose_dest: str = "/usr/local/bin/docker-compose",
        force: bool = False,
    ) -> None:
        """
        Install docker-compose

        :param docker_compose_version: compose version
        :param docker_compose_dest: install directory
        """
        self.docker_compose_version = docker_compose_version
        self.docker_compose_dest = docker_compose_dest
        self.force = force

    def get_validators(self) -> typing.List[validators.StepValidatorBase]:
        return [
            validators.CommandRequiredValidator("curl"),
        ]

    def run(self, c: Connection) -> None:
        from carnival.cmd import fs

        if not fs.is_file_exists(c, self.docker_compose_dest) or self.force:
            print("Installing docker-compose...")
            link = f"https://github.com/docker/compose/releases/download/{self.docker_compose_version}/docker-compose-`uname -s`-`uname -m`"
            cmd.cli.run(c, f"sudo curl -sL {link} -o {self.docker_compose_dest}")
            cmd.cli.run(c, f"sudo chmod a+x {self.docker_compose_dest}")
        else:
            print("docker-compose already installed...")


class UploadImageFile(Step):
    def __init__(
        self,
        docker_image_path: str,
        dest_dir: str = '/tmp/',
        rm_after_load: bool = False,
        rsync_opts: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ):
        pass
        """
        Upload docker image file and load into docker daemon, saved with `docker save image -o image.tar`

        :param docker_image_path: Docker image path
        :param dest_dir: Destination directory
        :param rm_after_load: Remove image after load to docker daemon
        """
        if not dest_dir.endswith("/"):
            dest_dir += "/"

        self.docker_image_path = docker_image_path
        self.dest_dir = dest_dir
        self.rm_after_load = rm_after_load
        self.rsync_opts = rsync_opts or {}

    def get_name(self) -> str:
        return f"{super().get_name()}(src={self.docker_image_path}, dst={self.dest_dir})"

    def get_validators(self) -> typing.List[validators.StepValidatorBase]:
        return [
            validators.CommandRequiredValidator("systemctl"),
            validators.CommandRequiredValidator("docker"),
        ]

    def run(self, c: Connection) -> None:
        image_file_name = os.path.basename(self.docker_image_path)
        systemd.Start("docker").run(c=c)

        cmd.transfer.rsync(c.host, self.docker_image_path, self.dest_dir, **self.rsync_opts)
        cmd.cli.run(c, f"cd {self.dest_dir}; docker load -i {image_file_name}")

        if self.rm_after_load:
            cmd.cli.run(c, f"rm -rf {self.dest_dir}{image_file_name}")
