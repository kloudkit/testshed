import contextlib

from python_on_whales import docker
from python_on_whales.exceptions import DockerException

from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.docker.container import Container


class Cleanup:
  @classmethod
  def run(
    cls,
    containers: list[Container] | None = None,
    labels: dict | None = None,
  ) -> None:
    """Force-remove all provided containers or labeled."""

    if containers is None:
      labels = labels or get_state().labels

      key, value = next(iter(labels.items()))

      containers = docker.container.list(
        all=True, filters=[("label", f"{key}={value}")]
      )

    for container in containers:
      with contextlib.suppress(DockerException):
        container.remove(force=True, volumes=True)
