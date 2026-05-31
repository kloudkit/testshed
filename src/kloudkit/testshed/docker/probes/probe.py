from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, replace
from typing import TYPE_CHECKING, Self


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

  def merge(self, other: "Probe", *, ignore_none: bool = True) -> Self:
    """Overlay another probe of the same type onto this one."""

    if not ignore_none:
      return replace(self, **asdict(other))

    overlay = {k: v for k, v in asdict(other).items() if v is not None}

    return replace(self, **overlay)

  @classmethod
  def resolve(
    cls,
    default: "Probe | None",
    user: "Probe | None",
    timeout: float | None = None,
  ) -> "Probe | None":
    """Resolve a final probe from default + override, overlaying timeout."""

    if user is ...:
      probe = default
    elif default is not None and type(default) is type(user):
      probe = default.merge(user)
    else:
      probe = user

    if timeout is not None and probe is not None:
      probe = replace(probe, timeout=timeout)

    return probe
