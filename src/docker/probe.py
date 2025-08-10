from dataclasses import asdict, dataclass, replace


@dataclass(slots=True)
class Probe:
  host: str = "http://localhost"
  port: int | None = None
  endpoint: str | None = None
  command: str = "curl"
  timeout: float = 30.0

  def merge(self, other: "Probe", *, ignore_none: bool = True) -> "Probe":
    """Merge two Probes."""

    if not ignore_none:
      return replace(self, **asdict(other))

    overlay = {k: v for k, v in asdict(other).items() if v is not None}

    return replace(self, **overlay)
