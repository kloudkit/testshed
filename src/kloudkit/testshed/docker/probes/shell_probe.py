from dataclasses import dataclass
from typing import TYPE_CHECKING

from kloudkit.testshed.docker.probes.probe import Probe


if TYPE_CHECKING:
  from kloudkit.testshed.docker.container import Container


@dataclass(slots=True)
class ShellProbe(Probe):
  command: str | list[str] = ""

  def check(self, container: "Container") -> None:
    """Single probe attempt. Raise on failure."""

    container.execute(self.command, raises=True)

  @property
  def failure_message(self) -> str:
    """Message shown on timeout."""

    return f"Command {self.command!r} did not succeed within {self.timeout}s"
