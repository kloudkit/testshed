from pathlib import Path
from typing import Iterable

from python_on_whales import Container as NativeContainer, docker

from kloudkit.testshed.docker.error_handler import error_handler
from kloudkit.testshed.docker.file import FileReader
from kloudkit.testshed.utils.models import Wrapper


class Container(Wrapper[NativeContainer]):
  @error_handler
  def execute(
    self,
    *args,
    raises=False,
    **kwargs,
  ) -> Iterable[tuple[str, bytes]] | str | None:
    """Wrap execution in `try/except`."""

    return self._wrapped.execute(*args, **kwargs)

  def ip(self) -> str:
    """Retrieve internal IP address of container."""

    return self.execute(["hostname", "-i"])

  @property
  def file(self) -> FileReader:
    """Higher order file reader."""

    return FileReader(self)

  def listdir(self, path: str | Path, *, hidden=False) -> tuple[str, ...]:
    """Retrieve directory listing for a given path."""

    flags = "-1"

    if hidden:
      flags = f"{flags}a"

    return tuple(self.execute(["\\ls", flags, str(path)]).splitlines())

  @classmethod
  def run(cls, *args, **kwargs):
    """Wrap the native `docker.run`."""

    instance = docker.run(*args, **kwargs)

    if isinstance(instance, str):
      return instance

    return cls(instance)
