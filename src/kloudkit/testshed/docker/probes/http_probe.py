from dataclasses import asdict, dataclass, replace
from typing import TYPE_CHECKING, Self

from kloudkit.testshed.docker.probes.probe import Probe


if TYPE_CHECKING:
  from kloudkit.testshed.docker.container import Container


@dataclass(slots=True)
class HttpProbe(Probe):
  host: str = "http://localhost"
  port: int | None = None
  endpoint: str | None = None
  command: str = "curl"

  @property
  def url(self) -> str:
    """Full target URL."""

    port = f":{self.port}" if self.port else ""
    endpoint = self.endpoint if self.endpoint else ""

    return "".join((self.host, port, endpoint))

  def check(self, container: "Container") -> None:
    """Single probe attempt. Raise on failure."""

    container.execute([*self.command.split(" "), self.url], raises=True)

  @property
  def failure_message(self) -> str:
    """Message shown on timeout."""

    return f"URL [{self.url}] was not reachable within {self.timeout}s"

  def merge(self, other: "HttpProbe", *, ignore_none: bool = True) -> Self:
    """Merge two Probes."""

    if not ignore_none:
      return replace(self, **asdict(other))

    overlay = {k: v for k, v in asdict(other).items() if v is not None}

    return replace(self, **overlay)
