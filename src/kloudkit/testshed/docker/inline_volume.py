import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class InlineVolume:
  """A volume mount created from inline content written to a temporary file."""

  path: Path | str
  _content: bytes | str
  _mode: int = 0o644
  _temp_path: Path | str | None = field(default=None, init=False, repr=False)

  def create(self) -> str:
    """Create the temporary file and return its path."""

    if self._temp_path is not None:
      return self._temp_path

    temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False)

    try:
      temp_file.write(self._content)
      temp_file.flush()

      self._temp_path = temp_file.name

      os.chmod(self._temp_path, self._mode)
    finally:
      temp_file.close()

    return self._temp_path

  def cleanup(self) -> None:
    """Clean up the temporary file."""

    if self._temp_path and Path(self._temp_path).exists():
      os.unlink(self._temp_path)
      self._temp_path = None
