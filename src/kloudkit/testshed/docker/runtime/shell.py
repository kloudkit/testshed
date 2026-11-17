from dataclasses import dataclass
from typing import Iterable

from python_on_whales import Container as NativeContainer
from python_on_whales.exceptions import DockerException, NoSuchContainer
from python_on_whales.utils import run

from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.runtime.error_handler import error_handler


@dataclass(frozen=True, slots=True)
class Result:
  exit_code: int
  stdout: str
  stderr: str

  @property
  def ok(self) -> bool:
    """Whether the command exited with `0`."""

    return self.exit_code == 0


class Shell(Wrapper[NativeContainer]):
  @error_handler
  def _execute(
    self,
    command: list[str] | tuple[str] | str,
    shell: str = None,
    login_shell: bool | None = None,
    check: bool = True,
    raises=False,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | Result | None:
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

    user = kwargs.pop("user", self._get("user"))

    if not check:
      return self._result(command, user=user, **kwargs)

    return self._wrapped.execute(command, user=user, **kwargs)

  def _result(self, command, *, user=None, workdir=None, envs=None) -> Result:
    """Run `docker exec` and keep the exit code, stdout and stderr."""

    cmd = self._wrapped.docker_cmd + ["exec"]

    cmd.add_simple_arg("--user", user)
    cmd.add_simple_arg("--workdir", workdir)
    cmd.add_args_mapping("--env", envs or {})
    cmd += [
      self._wrapped.id,
      *([command] if isinstance(command, str) else command),
    ]

    try:
      return Result(0, *run(cmd, return_stderr=True))
    except NoSuchContainer:
      raise
    except DockerException as error:
      return Result(
        error.return_code,
        (error.stdout or "").removesuffix("\n"),
        (error.stderr or "").removesuffix("\n"),
      )

  def bash(
    self,
    command: list[str] | tuple[str] | str,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | Result | None:
    """Execute commands using `bash` shell."""

    return self._execute(command, shell=self._get("bash_path"), **kwargs)

  def zsh(
    self,
    command: list[str] | tuple[str] | str,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | Result | None:
    """Execute commands using `zsh` shell."""

    return self._execute(command, shell=self._get("zsh_path"), **kwargs)

  def sh(
    self,
    command: list[str] | tuple[str] | str,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | Result | None:
    """Execute commands using `sh` shell."""

    return self._execute(command, shell=self._get("sh_path"), **kwargs)

  def __call__(
    self,
    command: list[str] | tuple[str] | str,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | Result | None:
    """Execute using the native method."""

    default_shell = (
      self._get("sh_path") if self._get("shell") is None else self._get("shell")
    )

    return self._execute(command, shell=default_shell, **kwargs)
