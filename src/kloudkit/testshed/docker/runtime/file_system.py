import json
import shlex
import tempfile
import tomllib
from pathlib import Path

import yaml
from python_on_whales import docker

from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.runtime.error_handler import error_handler


class FileSystem(Wrapper["Container"]):
  def _run(self, *argv: str | Path, **kwargs):
    """Run a command in the container with every argument quoted."""

    return self._wrapped.execute(shlex.join(map(str, argv)), **kwargs)

  def exists(self, path: str | Path) -> bool:
    """Check if a file or directory exists."""

    return self._run("test", "-e", path, check=False).ok

  def json(self, path: str | Path) -> dict:
    """Retrieve the content of a file as json."""

    return json.loads(self(path))

  def yaml(self, path: str | Path) -> dict:
    """Retrieve the content of a file as yaml."""

    return yaml.safe_load(self(path))

  def toml(self, path: str | Path) -> dict:
    """Retrieve the content of a file as toml."""

    return tomllib.loads(self(path))

  def writable(self, path: str | Path, **kwargs) -> bool:
    """Check whether the command's user can write to a path."""

    return self._run("test", "-w", path, check=False, **kwargs).ok

  def text(self, path: str | Path) -> str:
    """Retrieve the content of a file as text."""

    return self.bytes(path).decode("utf-8")

  @error_handler
  def bytes(self, path: str | Path) -> bytes:
    """Retrieve the content of a file as bytes."""

    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
      docker.copy((self._wrapped.id, path), tmp_file.name)

      return Path(tmp_file.name).read_bytes()

  @error_handler
  def ls(self, path: str | Path, *, hidden=False) -> tuple[str, ...]:
    """Retrieve directory listing for a given path."""

    flags = "-1"

    if hidden:
      flags = f"{flags}a"

    return tuple(self._run("command", "ls", flags, path).splitlines())

  @error_handler
  def _stat(self, path: str | Path, fmt: str) -> str:
    """Retrieve a `stat` format field for a given path."""

    return self._run("stat", "-c", fmt, path).strip()

  def mode(self, path: str | Path) -> str:
    """Retrieve the file or directory mode for a given path."""

    return self._stat(path, "%a")

  def owner(self, path: str | Path) -> str:
    """Retrieve the owning user for a given path."""

    return self._stat(path, "%U")

  def group(self, path: str | Path) -> str:
    """Retrieve the owning group for a given path."""

    return self._stat(path, "%G")

  def __call__(self, path: str | Path) -> str:
    """Retrieve the content of a file for a given path."""

    return self.text(path)
