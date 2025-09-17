import os
import random
import threading
from dataclasses import dataclass, field
from pathlib import Path


def _dynamic_network_name(project_name: str | None = None) -> str:
  """Generate a dynamic network name."""

  xdist_worker = os.getenv("PYTEST_XDIST_WORKER")
  random_suffix = f"{random.randint(1000, 9999)}"

  network_parts = filter(
    None,
    ["testshed", project_name or Path.cwd().name, random_suffix, xdist_worker],
  )

  return "-".join(network_parts)


@dataclass(slots=True)
class Options:
  labels: dict[str, str] = field(
    default_factory=lambda: {"com.kloudkit.testshed": "testing-container"}
  )
  network: str | None = None
  image: str | None = None
  tag: str = "tests"
  src_path: Path | None = None
  tests_path: Path | None = None
  stubs_path: Path | None = None

  @property
  def image_and_tag(self) -> str:
    """Fully-qualified Docker testing image for test runs."""

    sep = ":"

    if self.tag.startswith("sha"):
      sep = "@"

    return f"{self.image}{sep}{self.tag}"

  @classmethod
  def create(
    cls,
    project_name: str | None = None,
    image: str | None = None,
    tag: str = "tests",
    src_path: Path | None = None,
    tests_path: Path | None = None,
    stubs_path: Path | None = None,
  ) -> "Options":
    """Create an Options instance with a dynamic network name."""

    return cls(
      network=_dynamic_network_name(project_name),
      image=image,
      tag=tag,
      src_path=src_path,
      tests_path=tests_path,
      stubs_path=stubs_path,
    )


_state: Options | None = None
_state_lock = threading.RLock()


def get_state() -> Options:
  """Get the current state in a thread-safe manner."""

  with _state_lock:
    return Options() if _state is None else _state


def set_state(options: Options) -> None:
  """Set the global state in a thread-safe manner."""

  global _state
  with _state_lock:
    _state = options
