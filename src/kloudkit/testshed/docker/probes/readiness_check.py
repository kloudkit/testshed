import time

from python_on_whales.exceptions import DockerException

from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probes.http_probe import HttpProbe

import pytest


class ReadinessCheck:
  def __init__(self, container: Container, probe: HttpProbe):
    self._container: Container = container
    self._probe: HttpProbe = probe

  @property
  def command(self) -> list[str]:
    """Full probe test command."""

    return [*self._probe.command.split(" "), self._probe.url]

  def wait(self) -> None:
    """Wait until a container responds on the given endpoint."""

    deadline = time.time() + self._probe.timeout

    failure_message = (
      f"URL [{self._probe.url}] was not reachable within {self._probe.timeout}s"
    )

    while time.time() < deadline:
      try:
        self._container.execute(self.command, raises=True)

        return
      except DockerException:
        time.sleep(0.1)

    pytest.fail(failure_message, pytrace=False)
