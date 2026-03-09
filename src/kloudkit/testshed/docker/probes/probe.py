from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
  from kloudkit.testshed.docker.container import Container


@dataclass(slots=True)
class Probe(ABC):
  timeout: float = 30.0

  @abstractmethod
  def check(self, container: "Container") -> None:
    """Single probe attempt. Raise on failure."""

  @property
  @abstractmethod
  def failure_message(self) -> str:
    """Message shown on timeout."""

  @classmethod
  def resolve(
    cls,
    default: "Probe | None",
    user: "Probe | None",
    port: int | None = None,
  ) -> "Probe | None":
    """Resolve a final probe from default + user override + port."""
    from kloudkit.testshed.docker.probes.http_probe import HttpProbe

    probe = default

    if port is not None and isinstance(probe, HttpProbe):
      probe = probe.merge(HttpProbe(port=port))

    if user is ...:
      return probe

    if isinstance(probe, HttpProbe) and isinstance(user, HttpProbe):
      return probe.merge(user)

    return user
