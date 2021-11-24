import typing

from carnival import cmd, Step
from carnival.utils import log
from carnival import Connection
from carnival.exceptions import StepValidationError


class GetPackageVersions(Step):
    """
    Получить список доступных версий пакета
    """

    def __init__(self, pkgname: str):
        self.pkgname = pkgname

    def validate(self, c: Connection) -> None:
        if not cmd.cli.is_cmd_exist(c, "apt-cache"):
            raise StepValidationError("'apt-cache' is required")

    def run(self, c: Connection) -> typing.List[str]:
        versions = []
        result = cmd.cli.run(c, f"DEBIAN_FRONTEND=noninteractive apt-cache madison {self.pkgname}", hide=True, warn=True)
        if result.ok is False:
            return []

        for line in result.stdout.strip().split("\n"):
            n, ver, r = line.split("|")
            versions.append(ver.strip())
        return versions


class GetInstalledPackageVersion(Step):
    """
    Получить установленную версию пакета

    :return: Версия пакета если установлен, `None` если пакет не установлен
    """

    def __init__(self, pkgname: str):
        self.pkgname = pkgname

    def validate(self, c: Connection) -> None:
        if not cmd.cli.is_cmd_exist(c, "dpkg"):
            raise StepValidationError("'dpkg' is required")

    def run(self, c: Connection) -> typing.Optional[str]:
        """
        :return: Версия пакета если установлен, `None` если пакет не установлен
        """
        result = cmd.cli.run(c, f"DEBIAN_FRONTEND=noninteractive dpkg -l {self.pkgname}", hide=True, warn=True)
        if result.ok is False:
            return None
        installed, pkgn, ver, arch, *desc = result.stdout.strip().split("\n")[-1].split()
        if installed != 'ii':
            return None

        assert isinstance(ver, str)
        return ver.strip()


class IsPackageInstalled(Step):
    """
    Проверить установлен ли пакет
    Если версия не указана - проверяется любая
    """

    def __init__(self, pkgname: str, version: typing.Optional[str] = None) -> None:
        self.pkgname = pkgname
        self.version = version
        self.get_installed_package_version = GetInstalledPackageVersion(pkgname=self.pkgname)

    def validate(self, c: Connection) -> None:
        self.get_installed_package_version.validate(c=c)

    def run(self, c: Connection) -> bool:
        """
        Проверить установлен ли пакет
        Если версия не указана - проверяется любая
        """

        pkgver = self.get_installed_package_version.run(c=c)
        if self.version is None and pkgver is not None:
            return True

        if self.version is not None and pkgver == self.version:
            return True

        return False


class ForceInstall(Step):
    """
    Установить пакет без проверки установлен ли он
    """

    def __init__(self, pkgname: str, version: typing.Optional[str] = None, update: bool = False, hide: bool = False):
        self.pkgname = pkgname
        self.version = version
        self.update = update
        self.hide = hide

    def validate(self, c: Connection) -> None:
        if not cmd.cli.is_cmd_exist(c, "apt-get"):
            raise StepValidationError("'apt-get' is required")

    def run(self, c: Connection) -> None:
        if self.version:
            pkgname = f"{self.pkgname}={self.version}"

        if self.update:
            cmd.cli.run(c, "DEBIAN_FRONTEND=noninteractive sudo apt-get update", hide=self.hide)

        cmd.cli.run(c, f"DEBIAN_FRONTEND=noninteractive sudo apt-get install -y {pkgname}", hide=self.hide)


class Install(Step):
    """
    Установить пакет если он еще не установлен в системе
    """
    def __init__(self, pkgname: str, version: typing.Optional[str] = None, update: bool = True, hide: bool = False) -> None:
        """
        :param pkgname: название пакета
        :param version: версия
        :param update: запустить apt-get update перед установкой
        :param hide: скрыть вывод этапов
        """
        self.pkgname = pkgname
        self.version = version
        self.update = update
        self.hide = hide

        self.is_package_installed = IsPackageInstalled(pkgname=self.pkgname, version=self.version)
        self.force_install = ForceInstall(pkgname=self.pkgname, version=self.version, update=self.update, hide=self.hide)

    def validate(self, c: Connection) -> None:
        self.is_package_installed.validate(c=c)
        self.force_install.validate(c=c)

    def run(self, c: Connection) -> bool:
        """
        :return: `True` если пакет был установлен, `False` если пакет уже был установлен ранее
        """
        if self.is_package_installed.run(c=c):
            if self.version:
                if not self.hide:
                    log(f"{self.pkgname}={self.version} already installed", host=c.host)
            else:
                if not self.hide:
                    log(f"{self.pkgname} already installed", host=c.host)
            return False

        ForceInstall(pkgname=self.pkgname, version=self.version, update=self.update, hide=self.hide).run(c=c)
        return True


class InstallMultiple(Step):
    """
    Установить несколько пакетов, если они не установлены
    """

    def __init__(self, pkg_names: typing.List[str], update: bool = True, hide: bool = False) -> None:
        """
        :param pkg_names: список пакетов которые нужно установить
        :param update: запустить apt-get update перед установкой
        :param hide: скрыть вывод этапов
        """

        self.pkg_names = pkg_names
        self.update = update
        self.hide = hide

    def run(self, c: Connection) -> bool:
        """
        :return: `True` если хотя бы один пакет был установлен, `False` если все пакеты уже были установлен ранее
        """
        if all([IsPackageInstalled(x).run(c=c) for x in self.pkg_names]):
            if not self.hide:
                log(f"{','.join(self.pkg_names)} already installed", host=c.host)
            return False

        if self.update:
            cmd.cli.run(c, "DEBIAN_FRONTEND=noninteractive sudo apt-get update", hide=self.hide)

        for pkg in self.pkg_names:
            Install(pkgname=pkg, update=False, hide=self.hide).run(c=c)
        return True


class Remove(Step):
    """
    Удалить пакет
    """

    def __init__(self, pkg_names: typing.List[str], hide: bool = False) -> None:
        """
        :param pkg_names: список пакетов которые нужно удалить
        :param hide: скрыть вывод этапов
        """
        self.pkg_names = pkg_names
        self.hide = hide

    def validate(self, c: Connection) -> None:
        if not self.pkg_names:
            raise StepValidationError("pkg_names is empty")

        if not cmd.cli.is_cmd_exist(c, "apt-get"):
            raise StepValidationError("'apt-get' is required")

    def run(self, c: Connection) -> None:
        cmd.cli.run(c, f"DEBIAN_FRONTEND=noninteractive sudo apt-get remove --auto-remove -y {' '.join(self.pkg_names)}", hide=self.hide)
