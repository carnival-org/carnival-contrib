from carnival import Step
from carnival import cmd, log


class Install(Step):
    """
    Install caddy, set up systemd, put configuration
    """

    def run(
        self,
        dns_domain: str,
        caddyfile_template: str = 'carnival_contrib/caddy/Caddyfile',
        caddy_systemd_service_template: str = 'carnival_contrib/caddy/caddy.service',
        caddyfile_template_tls_email="user@example.com",
    ):
        if not cmd.fs.is_file_exists("/usr/local/bin/caddy"):
            log(f"Installing caddy")
            cmd.cli.run("curl https://getcaddy.com | bash -s personal http.grpc,http.ratelimit,http.realip", pty=True)

        if not cmd.fs.is_file_exists("/etc/systemd/system/caddy.service"):
            log(f"Setting up caddy")
            cmd.transfer.put_template(caddy_systemd_service_template, "/etc/systemd/system/caddy.service")
            cmd.fs.mkdirs("/etc/caddy", "/etc/ssl/caddy")
            cmd.systemd.daemon_reload()

        # if not cmd.transfer.is_file_exists("/etc/caddy/Caddyfile"):
        cmd.transfer.put_template(
            caddyfile_template, "/etc/caddy/Caddyfile",
            dns_domain=dns_domain,
            caddyfile_template_tls_email=caddyfile_template_tls_email
        )

        cmd.systemd.enable("caddy")
        cmd.systemd.restart("caddy")
