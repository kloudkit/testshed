import contextlib

from python_on_whales import docker
from python_on_whales.exceptions import DockerException

from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.docker.container import Container


class Cleanup:
  def __init__(self, state: ShedState):
    self._state = state

  def run(
    self,
    containers: list[Container] | None = None,
    labels: dict | None = None,
    network: bool = False,
  ) -> None:
    """Force-remove all provided containers or labeled."""

    if containers is None:
      labels = labels or self._state.labels

      key, value = next(iter(labels.items()))

      containers = docker.container.list(
        all=True, filters=[("label", f"{key}={value}")]
      )

    for container in containers:
      with contextlib.suppress(DockerException):
        container.remove(force=True, volumes=True)

    if network:
      with contextlib.suppress(DockerException):
        docker.network.remove(self._state.network)
