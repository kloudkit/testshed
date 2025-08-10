from pathlib import Path
from typing import Sequence

from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.docker.cleanup import Cleanup
from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probe import Probe
from kloudkit.testshed.docker.readiness import ReadinessProbe
from python_on_whales.components.volume.cli_wrapper import VolumeDefinition


class Factory:
  def __init__(self, *, test_root: Path | str):
    self._containers: list[Container] = []
    self._test_root: Path = Path(test_root)

  def __call__(self, *args, **kwargs) -> Container | str:
    """Delegate to `build`."""

    return self.build(*args, **kwargs)

  def build(
    self,
    image: str,
    *,
    detach: bool = True,
    probe: Probe | None = None,
    container_class: type[Container] | None = None,
    **kwargs,
  ) -> Container | str:
    """Create a Docker container to use in test-cases."""

    container_class = container_class or Container

    container = container_class.run(
      image,
      remove=True,
      labels=get_state().labels,
      detach=detach,
      networks=kwargs.pop("networks", [get_state().network]),
      volumes=self._normalize_volumes(kwargs.pop("volumes", [])),
      **kwargs,
    )

    if isinstance(container, str):
      return container

    self._containers.append(container)

    if probe:
      ReadinessProbe(container, probe).wait()

    return container

  def _normalize_volumes(
    self,
    volumes: Sequence[tuple[str | Path, str | Path]],
  ) -> list[VolumeDefinition]:
    """Resolve paths to `tests/stubs` when relative and mark as read-only."""

    stubs_dir = self._test_root / get_state().stubs_dir

    return [
      (
        str(source if Path(source).is_absolute() else stubs_dir / source),
        dest,
        "ro",
      )
      for source, dest in volumes
    ]

  def cleanup(self):
    """Force-remove all containers started during test-cases."""

    Cleanup.run(self._containers, get_state().labels)
