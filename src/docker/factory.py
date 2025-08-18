from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probes.http_probe import HttpProbe
from kloudkit.testshed.docker.probes.readiness_check import ReadinessCheck
from kloudkit.testshed.docker.runtime.cleanup import Cleanup
from kloudkit.testshed.docker.volume_manager import VolumeManager


class Factory:
  def __init__(self):
    self._containers: list[Container] = []
    self._volume_manager = VolumeManager()

  def __call__(self, *args, **kwargs) -> Container | str:
    """Delegate to `build`."""

    return self.build(*args, **kwargs)

  def build(
    self,
    image: str,
    *,
    detach: bool = True,
    probe: HttpProbe | None = None,
    container_class: type[Container] | None = None,
    test_name: str | None = None,
    **kwargs,
  ) -> Container | str:
    """Create a Docker container to use in test-cases."""

    container_class = container_class or Container

    container = container_class.run(
      image,
      remove=True,
      labels=self._prepare_labels(test_name),
      detach=detach,
      networks=kwargs.pop("networks", [get_state().network]),
      volumes=self._volume_manager.normalize(kwargs.pop("volumes", [])),
      **kwargs,
    )

    if isinstance(container, str):
      return container

    self._containers.append(container)

    if probe:
      ReadinessCheck(container, probe).wait()

    return container

  def _prepare_labels(self, test_name: str | None) -> dict:
    """Prepare labels to track Docker container instance."""

    labels = get_state().labels

    if test_name:
      labels["com.kloudkit.testshed.test"] = test_name

    return labels

  def cleanup(self) -> None:
    """Force-remove all containers started during test-cases."""

    Cleanup.run(self._containers, get_state().labels)

    self._volume_manager.cleanup()
