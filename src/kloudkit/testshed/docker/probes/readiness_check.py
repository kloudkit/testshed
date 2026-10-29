import contextlib
import time

from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probes.probe import Probe

import pytest


class ReadinessCheck:
  LOG_TAIL = 20

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
        exit_code = self._exit_code()

        if exit_code is not None:
          self._fail(self._exited_message(exit_code))

        time.sleep(0.1)

    self._fail(self._probe.failure_message)

  def _exit_code(self) -> int | None:
    """Exit code of the container once it stopped, `None` while it runs."""

    try:
      self._container.reload()
      state = self._container.state
    except Exception:
      return None

    return None if state.running else state.exit_code

  def _exited_message(self, exit_code: int) -> str:
    """Failure message for a container that exited before it was ready."""

    message = (
      f"Container exited with code {exit_code} before it was ready:"
      f" {self._probe.failure_message}"
    )

    with contextlib.suppress(Exception):
      logs = self._container.logs(tail=self.LOG_TAIL).rstrip()

      if logs:
        message += f"\n--- last {self.LOG_TAIL} lines of its logs ---\n{logs}"

    return message

  def _fail(self, message: str) -> None:
    """Fail the test, printing the container's logs when asked to."""

    if self._container_logs:
      with contextlib.suppress(Exception):
        self._container_logs(self._container.logs())

    pytest.fail(message, pytrace=False)
