import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from kloudkit.testshed.docker.probes.probe import Probe


if TYPE_CHECKING:
  from kloudkit.testshed.docker.container import Container


@dataclass(slots=True)
class LogProbe(Probe):
  pattern: str = ""

  def check(self, container: "Container") -> None:
    """Single probe attempt. Raise on failure."""

    logs = container.logs()
    if not re.search(self.pattern, logs):
      raise ValueError(f"Pattern {self.pattern!r} not found in logs")

  @property
  def failure_message(self) -> str:
    """Message shown on timeout."""

    return (
      f"Pattern {self.pattern!r} not found"
      f" in container logs within {self.timeout}s"
    )

