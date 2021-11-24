from carnival import Step
from carnival import Connection
from carnival import cmd, log

from carnival_contrib import systemd


class Install(Step):
    def __init__(
        self,
        caddyfile_template: str = 'carnival_contrib/caddy/Caddyfile',
        caddy_systemd_service_template: str = 'carnival_contrib/caddy/caddy.service',
        caddyfile_template_tls_email: str = "user@example.com",
    ):
        """
        Install caddy, set up systemd, put configuration

        :param caddyfile_template: Caddyfile template path
        :param caddy_systemd_service_template: caddy.service systemd file template path
        :param caddyfile_template_tls_email: tls email
        """
        self.caddyfile_template = caddyfile_template
        self.caddy_systemd_service_template = caddy_systemd_service_template
        self.caddyfile_template_tls_email = caddyfile_template_tls_email

    def run(self, c: Connection) -> None:
        if not cmd.fs.is_file_exists(c, "/usr/local/bin/caddy"):
            log("Installing caddy", host=c.host)
            cmd.cli.run(c, "curl https://getcaddy.com | bash -s personal http.grpc,http.ratelimit,http.realip")

        if not cmd.fs.is_file_exists(c, "/etc/systemd/system/caddy.service"):
            log("Setting up caddy", host=c.host)
            cmd.transfer.put_template(c, self.caddy_systemd_service_template, "/etc/systemd/system/caddy.service")
            cmd.fs.mkdirs(c, "/etc/caddy", "/etc/ssl/caddy")
            systemd.DaemonReload().run(c=c)

        # if not cmd.transfer.is_file_exists("/etc/caddy/Caddyfile"):
        cmd.transfer.put_template(
            c,
            self.caddyfile_template, "/etc/caddy/Caddyfile",
            caddyfile_template_tls_email=self.caddyfile_template_tls_email
        )

        systemd.Enable("caddy").run(c=c)
        systemd.Restart("caddy").run(c=c)
