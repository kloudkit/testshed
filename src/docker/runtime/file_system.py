import json
import tempfile
from pathlib import Path

import yaml
from python_on_whales import docker

from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.runtime.error_handler import error_handler


class FileSystem(Wrapper["Container"]):
  def exists(self, path: str | Path) -> bool:
    """Check if a file or directory exists."""

    result = self._wrapped.execute(
      ["test", "-e", path, "&&", "echo", "yes", "||", "echo", "no"]
    )

    return "yes" in result

  def json(self, path: str | Path) -> dict:
    """Retrieve the content of a file as json."""

    return json.loads(self(path))

  def yaml(self, path: str | Path) -> dict:
    """Retrieve the content of a file as yaml."""

    return yaml.safe_load(self(path))

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

    return tuple(
      self._wrapped.execute(["\\ls", flags, str(path)]).splitlines()
    )

  def __call__(self, path: str | Path) -> str:
    """Retrieve the content of a file for a given path."""

    return self.text(path)
