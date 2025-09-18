from pathlib import Path
from typing import Sequence

from python_on_whales.components.volume.cli_wrapper import VolumeDefinition

from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.docker.volumes.base_volume import BaseVolume


class VolumeManager:
  def __init__(self, state: ShedState):
    self._volume_objects: list[BaseVolume] = []
    self._state = state

  def _convert_from_volume_object(self, volume: BaseVolume) -> tuple[str, str]:
    self._volume_objects.append(volume)

    return (volume.create(), volume.path)

  def normalize(
    self,
    volumes: Sequence[tuple[str | Path, str | Path] | BaseVolume],
  ) -> list[VolumeDefinition]:
    """Resolve paths to `stubs` when relative and mark as read-only."""

    stubs_path = self._state.stubs_path
    normalized_volumes = []

    for volume in volumes:
      if isinstance(volume, BaseVolume):
        volume = self._convert_from_volume_object(volume)

      source, dest = volume

      source_path = str(
        source if Path(source).is_absolute() else stubs_path / source
      )

      normalized_volumes.append((source_path, dest, "ro"))

    return normalized_volumes

  def cleanup(self) -> None:
    """Clean up volume object temporary files."""

    for volume_object in self._volume_objects:
      volume_object.cleanup()

    self._volume_objects.clear()
