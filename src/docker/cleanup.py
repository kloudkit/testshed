import contextlib

from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.docker.container import Container
from python_on_whales import docker
from python_on_whales.exceptions import NoSuchContainer


class Cleanup:
  @classmethod
  def run(
    cls,
    containers: list[Container] | None = None,
    labels: dict | None = None,
  ) -> None:
    """Force-remove all provided containers or labeled."""

    labels = labels or get_state().labels

    if not containers:
      key, value = next(iter(labels.items()))

      containers = docker.container.list(
        all=True, filters=[("label", f"{key}={value}")]
      )

    for container in containers:
      with contextlib.suppress(NoSuchContainer):
        container.remove(force=True, volumes=True)
