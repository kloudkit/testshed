import contextlib
import time

from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probes.probe import Probe

import pytest


class ReadinessCheck:
  def __init__(
    self, container: Container, probe: Probe, *, container_logs=None
  ):
    self._container: Container = container
    self._probe: Probe = probe
    self._container_logs = container_logs

  def wait(self) -> None:
    """Wait until a container passes the probe check."""

    deadline = time.time() + self._probe.timeout

    while time.time() < deadline:
      try:
        self._probe.check(self._container)

        return
      except Exception:
        time.sleep(0.1)

    if self._container_logs:
      with contextlib.suppress(Exception):
        self._container_logs(self._container.logs())

    pytest.fail(self._probe.failure_message, pytrace=False)
