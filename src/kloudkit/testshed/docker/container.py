from typing import Callable

from python_on_whales import Container as NativeContainer, docker

from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.probes.probe import Probe
from kloudkit.testshed.docker.probes.readiness_check import ReadinessCheck
from kloudkit.testshed.docker.runtime.file_system import FileSystem
from kloudkit.testshed.docker.runtime.process import Process
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

    result = self.execute(["hostname", "-i"], check=False)

    if result.ok:
      return result.stdout

    settings = self._wrapped.network_settings

    return (
      next(iter(settings.networks.values())).ip_address
      if settings.networks
      else settings.ip_address
    )

  def whoami(self) -> str:
    """Retrieve the current user inside the container."""

    return self.execute(["whoami"], raises=True)

  def env(self, name: str | None = None, **kwargs) -> dict | str | None:
    """Retrieve the environment commands see, after shell activation."""

    environ = self.proc.environ("self", **kwargs)

    return environ if name is None else environ.get(name)

  def wait(
    self, probe: Probe | None = None, *, timeout: float | None = None
  ) -> None:
    """Wait until `probe`, or the probe the container started with, passes."""

    probe = Probe.resolve(
      self._get("probe"), ... if probe is None else probe, timeout
    )

    if probe is None:
      raise ValueError("no probe to wait for: pass one, or start with one")

    ReadinessCheck(
      self, probe, container_logs=self._get("container_logs")
    ).wait()

  @property
  def fs(self) -> FileSystem:
    """Higher order file system."""

    return FileSystem(self)

  @property
  def proc(self) -> Process:
    """Higher order process inspection."""

    return Process(self)

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
      container_logs=getattr(self._args, "container_logs", False),
    )

  def __repr__(self) -> str:
    name = getattr(self._wrapped, "name", None)
    cid = getattr(self._wrapped, "id", None)

    parts = []

    if name:
      parts.append(f"name={name!r}")

    if cid:
      parts.append(f"id={cid[:8]!r}")

    inner = ", ".join(parts) if parts else repr(self._wrapped)

    return f"{type(self).__name__}({inner})"

  @classmethod
  def run(cls, *args, **kwargs):
    """Wrap the native `docker.run`."""

    container_logs = kwargs.pop("container_logs", False)
    probe = kwargs.pop("probe", None)

    instance = docker.run(*args, **kwargs)

    if isinstance(instance, str):
      return instance

    return cls(instance, container_logs=container_logs, probe=probe)

  @classmethod
  def attach(
    cls,
    name_or_id: str,
    *,
    container_logs: Callable[[str], None] | None = None,
  ) -> "Container":
    """Wrap an existing, externally-managed container."""

    instance = docker.container.inspect(name_or_id)

    return cls(instance, container_logs=container_logs)
