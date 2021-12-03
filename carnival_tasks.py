import typing

from carnival import SshHost, Host, Step, Role, Task
from carnival_contrib import apt, transfer


class ServerRole(Role):
    def __init__(self, host: Host):
        super(ServerRole, self).__init__(host)
        self.packages = ['htop', 'mc']


class ServerTask(Task[ServerRole]):
    def get_steps(self) -> typing.List["Step"]:
        return [
            apt.InstallMultiple(self.role.packages),
            transfer.GetFile("/etc/fstab", "./remotes/fstab"),
            transfer.PutFile("/etc/hosts", "/root/remotes/hosts"),
        ]


test1 = SshHost("185.103.134.116", ssh_user="root")
test2 = SshHost("185.103.134.162", ssh_user="root")

ServerRole(test1)
ServerRole(test2)
