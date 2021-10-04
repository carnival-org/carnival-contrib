import os
from typing import List, Dict, Any, Optional, Union, Tuple

from carnival import Step
from carnival import cmd


class DeployComposeService(Step):
    def run(
            self,
            app_dir: str,

            template_files: List[Union[str, Tuple[str, str]]],
            template_context: Dict[str, Any],

            scale: Optional[Dict[str, int]] = None,
            start_service=True,
    ):
        """
        Upload docker-compose service and related files.

        :param app_dir: Application remote destination directory
        :param template_files: List of templates to upload. Can be file name or tuple (source_file, dest_file_name)
        :param template_context: template files context
        :param scale: scale service when start. for example 'webapp=2 redis=2'
        :param start_service: start service after upload
        """
        cmd.cli.run(f"mkdir -p {app_dir}")
        cmd.systemd.start("docker")

        for dest in template_files:
            if isinstance(dest, str):
                source_file = dest
                dest_fname = os.path.basename(source_file)
            elif isinstance(dest, tuple):
                source_file, dest_fname = dest
            else:
                raise ValueError(f"Cant parse template_file definition: {dest}")

            cmd.transfer.put_template(
                source_file, os.path.join(app_dir, dest_fname),
                **template_context
            )

        cmd.cli.pty(f"cd {app_dir}; docker-compose rm -f")

        if start_service:
            if scale:
                scale_str = " ".join([f" --scale {service_name}={count}" for service_name, count in scale.items()])
            else:
                scale_str = ""
            cmd.cli.pty(f"cd {app_dir}; docker-compose up -d --remove-orphans {scale_str}")


class DockerRestartService(Step):
    def run(self, app_dir: str):
        """
        Restart compose service

        :param app_dir: Application remote directory
        """
        cmd.cli.pty(f"cd {app_dir}; docker-compose restart")
