from carnival import cmd, Step
from carnival import Connection


class DaemonReload(Step):
    """
    Перегрузить systemd
    """

    def run(self, c: Connection) -> None:
        cmd.cli.run(c, "sudo systemctl --system daemon-reload")


class Start(Step):
    """
    Запустить сервис
    """
    def __init__(self, service_name: str, reload_daemon: bool = False) -> None:
        """
        :param service_name: имя сервиса
        :param reload_daemon: перегрузить systemd
        """
        self.service_name = service_name
        self.reload_daemon = reload_daemon

    def run(self, c: Connection) -> None:
        if self.reload_daemon:
            DaemonReload().run(c=c)

        cmd.cli.run(c, f"sudo systemctl start {self.service_name}")


class Stop(Step):
    """
    Остановить сервис
    """

    def __init__(self, service_name: str, reload_daemon: bool = False) -> None:
        """
        :param service_name: имя сервиса
        :param reload_daemon: перегрузить systemd
        """
        self.service_name = service_name
        self.reload_daemon = reload_daemon

    def run(self, c: Connection) -> None:
        if self.reload_daemon:
            DaemonReload().run(c=c)

        cmd.cli.run(c, f"sudo systemctl stop {self.service_name}")


class Restart(Step):
    """
    Перезапустить сервис
    """

    def __init__(self, service_name: str) -> None:
        """
        :param service_name: имя сервиса
        """
        self.service_name = service_name

    def run(self, c: Connection) -> None:
        cmd.cli.run(c, f"sudo systemctl restart {self.service_name}")


class Enable(Step):
    """
    Добавить сервис в автозапуск
    """

    def __init__(self, service_name: str, reload_daemon: bool = False, start_now: bool = True) -> None:
        """
        :param service_name: имя сервиса
        :param reload_daemon: перегрузить systemd
        :param start_now: запустить сервис после добавления
        """
        self.service_name = service_name
        self.reload_daemon = reload_daemon
        self.start_now = start_now

    def run(self, c: Connection) -> None:
        if self.reload_daemon:
            DaemonReload().run(c=c)

        cmd.cli.run(c, f"sudo systemctl enable {self.service_name}")

        if self.start_now:
            Start(self.service_name).run(c=c)


class Disable(Step):
    """
    Убрать сервис из автозапуска
    """

    def __init__(self, service_name: str, reload_daemon: bool = False, stop_now: bool = True) -> None:
        """
        :param service_name: имя сервиса
        :param reload_daemon: перегрузить systemd
        :param stop_now: Остановить сервис
        """

        self.service_name = service_name
        self.reload_daemon = reload_daemon
        self.stop_now = stop_now

    def run(self, c: Connection) -> None:
        if self.reload_daemon:
            DaemonReload().run(c=c)

        cmd.cli.run(c, f"sudo systemctl disable {self.service_name}")

        if self.stop_now:
            Stop(self.service_name).run(c=c)
