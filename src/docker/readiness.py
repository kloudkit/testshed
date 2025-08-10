import time
from typing import TYPE_CHECKING

from kloudkit.testshed.docker.container import Container
from python_on_whales.exceptions import DockerException, NoSuchContainer

import pytest


if TYPE_CHECKING:
  from kloudkit.testshed.docker.probes import Probe


class ReadinessProbe:
  def __init__(self, container: Container, probe: "Probe"):
    self._container: Container = container
    self._probe: "Probe" = probe

  @property
  def url(self) -> str:
    """Full probe target URL."""

    port = f":{self._probe.port}" if self._probe.port else ""
    endpoint = self._probe.endpoint if self._probe.endpoint else ""

    return "".join((self._probe.host, port, endpoint))

  @property
  def command(self) -> list[str]:
    """Full probe test command."""

    return [*self._probe.command.split(" "), self.url]

  def wait(self) -> None:
    """Wait until a container responds on the given endpoint."""

    deadline = time.time() + self._probe.timeout

    failure_message = (
      f"URL [{self.url}] was not reachable within {self._probe.timeout}s"
    )

    while time.time() < deadline:
      try:
        self._container.execute(self.command)

        return
      except NoSuchContainer:
        failure_message = "Container exited unexpectedly before the timeout"
        break
      except DockerException:
        time.sleep(0.1)

    pytest.fail(failure_message, pytrace=False)
