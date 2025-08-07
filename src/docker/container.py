from pathlib import Path

from python_on_whales import Container as NativeContainer, docker

from kloudkit.testshed.docker.file import FileReader


class Container:
  def __init__(self, container: NativeContainer):
    self._container = container

  def __getattr__(self, name):
    return getattr(self._container, name)

  def ip(self) -> str:
    """Retrieve internal IP address of container."""

    return self.execute(["hostname", "-i"])

  @property
  def file(self) -> FileReader:
    """Higher order file reader."""

    return FileReader(self)

  def listdir(self, path: str | Path, *, hidden=False) -> tuple[str]:
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
