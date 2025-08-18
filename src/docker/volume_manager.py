from pathlib import Path
from typing import Sequence

from python_on_whales.components.volume.cli_wrapper import VolumeDefinition

from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.docker.inline_volume import InlineVolume


class VolumeManager:
  def __init__(self):
    self._inline_volumes: list[InlineVolume] = []

  def _convert_from_inline(self, volume: InlineVolume) -> tuple[str, str]:
    self._inline_volumes.append(volume)

    return (volume.create(), volume.path)

  def normalize(
    self,
    volumes: Sequence[tuple[str | Path, str | Path] | InlineVolume],
  ) -> list[VolumeDefinition]:
    """Resolve paths to `stubs` when relative and mark as read-only."""

    stubs_path = get_state().stubs_path
    normalized_volumes = []

    for volume in volumes:
      if isinstance(volume, InlineVolume):
        volume = self._convert_from_inline(volume)

      source, dest = volume

      source_path = str(
        source if Path(source).is_absolute() else stubs_path / source
      )

      normalized_volumes.append((source_path, dest, "ro"))

    return normalized_volumes

  def cleanup(self) -> None:
    """Clean up InlineVolume temporary files."""

    for inline_volume in self._inline_volumes:
      inline_volume.cleanup()

    self._inline_volumes.clear()
