import os.path
import typing
from io import BytesIO
from hashlib import sha1

from colorama import Style as S, Fore as F  # type: ignore

from fabric.transfer import Transfer  # type: ignore

from carnival import Connection, localhost_connection
from carnival.templates import render
from carnival.steps import shortcuts, Step, validators


def _file_sha1sum(c: Connection, fpath: str) -> typing.Optional[str]:
    if not shortcuts.is_file(c, fpath):
        return None
    return c.run(f"cat {fpath} | shasum -a1", hide=True).stdout.strip(" -\t\n")


class GetFile(Step):
    """
    Скачать файл с удаленного сервера на локальный диск
    """
    def __init__(self, remote_path: str, local_path: str):
        """
        :param remote_path: Путь до файла на сервере
        :param local_path: Локальный путь назначения
        """
        self.remote_path = remote_path
        self.local_path = local_path

    def get_name(self) -> str:
        return f"{super().get_name()}(remote_path={self.remote_path}, local_path={self.local_path})"

    def get_validators(self) -> typing.List["validators.StepValidatorBase"]:
        return [
            validators.IsFileValidator(self.remote_path),
            validators.Not(
                validators.IsDirectoryValidator(self.local_path, on_localhost=True),
                error_message=f"{self.remote_path} must be full file path, not directory",
            )
        ]

    def run(self, c: "Connection") -> None:
        # <https://docs.fabfile.org/en/2.5/api/transfer.html#fabric.transfer.Transfer.get>
        # TODO: c._c ;(
        t = Transfer(c._c)  # type: ignore

        remote_sha1 = _file_sha1sum(c, self.remote_path)
        local_sha1 = _file_sha1sum(localhost_connection, self.local_path)
        if remote_sha1 is not None and local_sha1 is not None:
            if remote_sha1 == local_sha1:
                print(f"{S.BRIGHT}{self.remote_path}{S.RESET_ALL}: {F.GREEN}not changed{F.RESET}")
                return

        # Create dirs if needed
        dirname = os.path.dirname(self.local_path)
        localhost_connection.run(f"mkdir -p {dirname}", hide=True)

        t.get(remote=self.remote_path, local=self.local_path)
        print(f"{S.BRIGHT}{self.remote_path}{S.RESET_ALL}: {F.YELLOW}downloaded{F.RESET}")


class PutFile(Step):
    """
    Закачать файл на сервер

    """
    def __init__(self, local_path: str, remote_path: str, ):
        """
        :param local_path: путь до локального файла
        :param remote_path: путь куда сохранить на сервере
        """
        self.local_path = local_path
        self.remote_path = remote_path

    def get_name(self) -> str:
        return f"{super().get_name()}(local_path={self.local_path}, remote_path={self.remote_path})"

    def get_validators(self) -> typing.List["validators.StepValidatorBase"]:
        return [
            validators.IsFileValidator(self.local_path, on_localhost=True),
            validators.Not(
                validators.IsDirectoryValidator(self.remote_path),
                error_message=f"{self.remote_path} must be full file path, not directory",
            )
        ]

    def run(self, c: "Connection") -> None:
        # <https://docs.fabfile.org/en/2.5/api/transfer.html#fabric.transfer.Transfer.put>
        # TODO: c._c ;(
        t = Transfer(c._c)  # type: ignore

        remote_sha1 = _file_sha1sum(c, self.remote_path)
        local_sha1 = _file_sha1sum(localhost_connection, self.local_path)
        if remote_sha1 is not None and local_sha1 is not None:
            if remote_sha1 == local_sha1:
                print(f"{S.BRIGHT}{self.remote_path}{S.RESET_ALL}: {F.GREEN}not changed{F.RESET}")
                return

        # Create dirs if needed
        dirname = os.path.dirname(self.remote_path)
        c.run(f"mkdir -p {dirname}", hide=True)

        t.put(local=self.local_path, remote=self.remote_path)
        print(f"{S.BRIGHT}{self.remote_path}{S.RESET_ALL}: {F.YELLOW}uploaded{F.RESET}")


class PutTemplate(Step):
    """
    Отрендерить файл с помощью jinja-шаблонов и закачать на сервер
    См раздел templates.
    """

    def __init__(self, template_path: str, remote_path: str, context: typing.Dict[str, typing.Any]):
        """
        :param template_path: путь до локального файла jinja
        :param remote_path: путь куда сохранить на сервере
        :param context: контекс для рендеринга jinja2
        """
        self.template_path = template_path
        self.remote_path = remote_path
        self.context = context

    def get_name(self) -> str:
        return f"{super().get_name()}(template_path={self.template_path})"

    def get_validators(self) -> typing.List["validators.StepValidatorBase"]:
        return [
            validators.TemplateValidator(self.template_path, context=self.context),
        ]

    def run(self, c: "Connection") -> None:
        filestr = render(template_path=self.template_path, **self.context)
        remote_sha1 = _file_sha1sum(c, self.remote_path)
        local_sha1 = sha1(filestr.encode()).hexdigest()

        if remote_sha1 is not None and local_sha1 is not None:
            if remote_sha1 == local_sha1:
                print(f"{S.BRIGHT}{self.template_path}{S.RESET_ALL}: {F.GREEN}not changed{F.RESET}")
                return

        # Create dirs if needed
        dirname = os.path.dirname(self.remote_path)
        c.run(f"mkdir -p {dirname}", hide=True)

        # TODO: c._c ;(
        t = Transfer(c._c)  # type: ignore
        t.put(local=BytesIO(filestr.encode()), remote=self.remote_path)

        print(f"{S.BRIGHT}{self.template_path}{S.RESET_ALL}: {F.YELLOW}uploaded{F.RESET}")


__all__ = (
    "GetFile",
    "PutFile",
    "PutTemplate",
)
