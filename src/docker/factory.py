from pathlib import Path
from typing import Sequence

from python_on_whales.components.volume.cli_wrapper import VolumeDefinition

from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.docker.cleanup import Cleanup
from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probe import Probe
from kloudkit.testshed.docker.readiness import ReadinessProbe


class Factory:
  def __init__(self):
    self._containers: list[Container] = []

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
    test_name: str | None = None,
    scope: str | None = None,
    **kwargs,
  ) -> Container | str:
    """Create a Docker container to use in test-cases."""

    container_class = container_class or Container

    container = container_class.run(
      image,
      remove=True,
      labels=self._prepare_labels(test_name, scope),
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

  def _prepare_labels(self, test_name: str | None, scope: str | None) -> dict:
    """Prepare labels to track Docker container instance."""

    labels = get_state().labels

    if test_name:
      labels["com.kloudkit.testshed.test"] = test_name

    if scope:
      labels["com.kloudkit.testshed.scope"] = scope

    return labels

  def _normalize_volumes(
    self,
    volumes: Sequence[tuple[str | Path, str | Path]],
  ) -> list[VolumeDefinition]:
    """Resolve paths to `stubs` when relative and mark as read-only."""

    stubs_path = get_state().stubs_path

    return [
      (
        str(source if Path(source).is_absolute() else stubs_path / source),
        dest,
        "ro",
      )
      for source, dest in volumes
    ]

  def cleanup(self) -> None:
    """Force-remove all containers started during test-cases."""

    Cleanup.run(self._containers, get_state().labels)
