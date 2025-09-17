from dataclasses import dataclass

from kloudkit.testshed.docker.volumes.base_volume import BaseVolume


@dataclass
class InlineVolume(BaseVolume):
  def __init__(self, path, content, *, mode=0o644):
    super().__init__(path, _mode=mode)
    self._content = content

  def _get_content(self) -> bytes:
    """Get the inline content as bytes."""

    if isinstance(self._content, str):
      return self._content.encode("utf-8")

    return self._content
