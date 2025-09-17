import os
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BaseVolume(ABC):
  path: Path | str
  _mode: int = 0o644
  _temp_path: Path | str | None = field(default=None, init=False, repr=False)

  def create(self) -> str:
    """Create the temporary file and return its path."""

    if self._temp_path is not None:
      return self._temp_path

    content = self._get_content()
    self._temp_path = self._create_temp_file(content)

    os.chmod(self._temp_path, self._mode)

    return self._temp_path

  def cleanup(self) -> None:
    """Clean up the temporary file."""

    if self._temp_path and Path(self._temp_path).exists():
      os.unlink(self._temp_path)
      self._temp_path = None

  def _create_temp_file(self, content: bytes) -> str:
    """Create a temporary file with the given content."""

    temp_file = tempfile.NamedTemporaryFile(mode="wb", delete=False)

    try:
      temp_file.write(content)
      temp_file.flush()

      return temp_file.name
    finally:
      temp_file.close()

  @abstractmethod
  def _get_content(self) -> bytes:
    """Get the content to write to the temporary file."""
    ...
