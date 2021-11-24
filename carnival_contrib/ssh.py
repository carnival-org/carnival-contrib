import typing
import os

from carnival import Step, cmd
from carnival import Connection


class AddAuthorizedKey(Step):
    """
    Добавить ssh ключ в `authorized_keys` если его там нет
    """

    def __init__(self, ssh_key: str, keys_file: str = ".ssh/authorized_keys") -> None:
        """
        :param ssh_key: ключ
        :param keys_file: пусть до файла `authorized_keys`
        :return: `True` если ключ был добавлен, `False` если ключ уже был в файле
        """
        self.ssh_key = ssh_key.strip()
        self.keys_file = keys_file

    def run(self, c: Connection) -> bool:
        cmd.cli.run(c, "mkdir -p ~/.ssh")
        cmd.cli.run(c, "chmod 700 ~/.ssh")
        cmd.cli.run(c, f"touch {self.keys_file}")

        if not cmd.fs.is_file_contains(c, self.keys_file, self.ssh_key, escape=True):
            cmd.cli.run(c, f"echo '{self.ssh_key}' >> {self.keys_file}")
            return True
        return False


class GetAuthorizedKeys(Step):
    """
    Получить список авторизованных ssh-ключей сервера
    """

    def run(self, c: Connection) -> typing.List[str]:
        if cmd.fs.is_file_exists(c, "~/.ssh/authorized_keys") is False:
            return []

        keys_file: str = cmd.cli.run(c, "cat ~/.ssh/authorized_keys", hide=True).stdout.strip()
        return keys_file.split("\n")


class CopyId(Step):
    """
    Добавить публичный ssh-ключ текущего пользователя в авторизованные
    """

    def __init__(self, pubkey_file: str = "~/.ssh/id_rsa.pub") -> None:
        """
        :param pubkey_file: путь до файла с публичным ключем
        :return: `True` если ключ был добавлен, `False` если ключ уже был в файле
        """
        self.pubkey_file = pubkey_file

    def run(self, c: Connection) -> bool:
        key = open(os.path.expanduser(self.pubkey_file)).read().strip()
        return AddAuthorizedKey(key).run(c=c)
