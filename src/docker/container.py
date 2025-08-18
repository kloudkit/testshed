from python_on_whales import Container as NativeContainer, docker

from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.runtime.file_system import FileSystem
from kloudkit.testshed.docker.runtime.shell import Shell


class Container(Wrapper[NativeContainer]):
  BASH_PATH = "/bin/bash"
  SH_PATH = "/bin/sh"
  ZSH_PATH = "/usr/bin/zsh"

  LOGIN_SHELL = False
  DEFAULT_USER = None
  DEFAULT_SHELL = None

  def ip(self) -> str:
    """Retrieve internal IP address of container."""

    return self.execute(["hostname", "-i"])

  @property
  def fs(self) -> FileSystem:
    """Higher order file system."""

    return FileSystem(self)

  @property
  def execute(self) -> Shell:
    """Higher order execution."""

    return Shell(
      self._wrapped,
      bash_path=self.BASH_PATH,
      sh_path=self.SH_PATH,
      zsh_path=self.ZSH_PATH,
      user=self.DEFAULT_USER,
      shell=self.DEFAULT_SHELL,
      login_shell=self.LOGIN_SHELL,
    )

  @classmethod
  def run(cls, *args, **kwargs):
    """Wrap the native `docker.run`."""

    instance = docker.run(*args, **kwargs)

    if isinstance(instance, str):
      return instance

    return cls(instance)
