from typing import Iterable

from python_on_whales import Container as NativeContainer

from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.runtime.error_handler import error_handler


class Shell(Wrapper[NativeContainer]):
  def _get(self, name: str, default=None):
    """Get argument with fallback to default."""

    return getattr(self._args, name, default)

  @error_handler
  def _execute(
    self,
    command: list[str] | tuple[str] | str,
    shell: str = None,
    login_shell: bool | None = None,
    raises=False,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | None:
    """Execute commands natively using the default shell."""

    flags = (
      "-cli"
      if (
        login_shell
        if login_shell is not None
        else self._get("login_shell", False)
      )
      else "-c"
    )

    shell = shell or self._get("shell")

    if shell:
      if not isinstance(command, str):
        command = " ".join(command)

      command = [shell, flags, command]

    return self._wrapped.execute(
      command, user=kwargs.pop("user", self._get("user")), **kwargs
    )

  def bash(
    self,
    command: list[str] | tuple[str] | str,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | None:
    """Execute commands using `bash` shell."""

    return self._execute(command, shell=self._get("bash_path"), **kwargs)

  def zsh(
    self,
    command: list[str] | tuple[str] | str,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | None:
    """Execute commands using `zsh` shell."""

    return self._execute(command, shell=self._get("zsh_path"), **kwargs)

  def sh(
    self,
    command: list[str] | tuple[str] | str,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | None:
    """Execute commands using `sh` shell."""

    return self._execute(command, shell=self._get("sh_path"), **kwargs)

  def __call__(
    self,
    command: list[str] | tuple[str] | str,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | None:
    """Execute using the native method."""

    default_shell = (
      self._get("sh_path") if self._get("shell") is None else self._get("shell")
    )

    return self._execute(command, shell=default_shell, **kwargs)
