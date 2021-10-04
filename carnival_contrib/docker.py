import os

from carnival import Step
from carnival import cmd
from carnival.utils import log


class CeInstallUbuntu(Step):
    def run(self, docker_version=None):
        """
        Install docker-ce on ubuntu

        :param docker_version: docker-ce version to install
        :return: True if installed, False if was already installed
        """
        # https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/
        from carnival.cmd import apt
        pkgname = "docker-ce"
        if apt.is_pkg_installed(pkgname, docker_version):
            log(f"{pkgname} already installed")
            return False

        log(f"Installing {pkgname}...")

        cmd.cli.run("sudo apt-get update")
        cmd.cli.run("sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common")
        cmd.cli.run("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -", pty=True)
        cmd.cli.run('sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')

        apt.force_install(pkgname=pkgname, version=docker_version, update=True, hide=True)
        return True


class ComposeInstall(Step):
    def run(self, docker_compose_version="1.25.1", docker_compose_dest="/usr/local/bin/docker-compose", force=False):
        """
        Install docker-compose

        :param docker_compose_version: compose version
        :param docker_compose_dest: install directory
        """
        from carnival.cmd import fs

        if not fs.is_file_exists(docker_compose_dest) or force:
            log("Installing docker-compose...")
            link = f"https://github.com/docker/compose/releases/download/{docker_compose_version}/docker-compose-`uname -s`-`uname -m`"
            cmd.cli.run(f"sudo curl -sL {link} -o {docker_compose_dest}")
            cmd.cli.run(f"sudo chmod a+x {docker_compose_dest}")
        else:
            log("docker-compose already installed...")


class DockerUploadImageFile(Step):
    def run(self, docker_image_path, dest_dir='/tmp/', rm_after_load=False, rsync_opts=None):
        """
        Upload docker image file and load into docker daemon, saved with `docker save image -o image.tar`

        :param docker_image_path: Docker image path
        :param dest_dir: Destination directory
        :param rm_after_load: Remove image after load to docker daemon
        """
        if not dest_dir.endswith("/"):
            dest_dir += "/"

        image_file_name = os.path.basename(docker_image_path)

        cmd.systemd.start("docker")
        cmd.transfer.rsync(docker_image_path, dest_dir, **rsync_opts or {})
        cmd.cli.pty(f"cd {dest_dir}; docker load -i {image_file_name}")

        if rm_after_load:
            cmd.cli.pty(f"rm -rf {dest_dir}{image_file_name}")
