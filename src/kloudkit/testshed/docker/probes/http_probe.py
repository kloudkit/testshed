from dataclasses import asdict, dataclass, replace
from typing import Self


@dataclass(slots=True)
class HttpProbe:
  host: str = "http://localhost"
  port: int | None = None
  endpoint: str | None = None
  command: str = "curl"
  timeout: float = 30.0

  @property
  def url(self) -> str:
    """Full target URL."""

    port = f":{self.port}" if self.port else ""
    endpoint = self.endpoint if self.endpoint else ""

    return "".join((self.host, port, endpoint))

  def merge(
    self, other: "HttpProbe", *, ignore_none: bool = True
  ) -> Self:
    """Merge two Probes."""

    if not ignore_none:
      return replace(self, **asdict(other))

    overlay = {k: v for k, v in asdict(other).items() if v is not None}

    return replace(self, **overlay)
