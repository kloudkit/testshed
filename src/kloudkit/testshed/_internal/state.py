import os
import random
import threading
from dataclasses import dataclass
from pathlib import Path


def _generate_instance_key(project_name: str) -> str:
  """Generate a unique instance identifier for containers and networks."""

  xdist_worker = os.getenv("PYTEST_XDIST_WORKER")
  random_suffix = f"{random.randint(1000, 9999)}"

  instance_parts = filter(
    None,
    ["testshed", project_name, random_suffix, xdist_worker],
  )

  return "-".join(instance_parts)


@dataclass(slots=True)
class Options:
  instance_key: str
  image: str | None = None
  tag: str = "tests"
  src_path: Path | None = None
  tests_path: Path | None = None
  stubs_path: Path | None = None

  @property
  def labels(self) -> dict[str, str]:
    """Labels for tracking Docker containers."""

    return {"com.kloudkit.testshed": self.instance_key}

  @property
  def network(self) -> str:
    """Network name for Docker containers."""

    return self.instance_key

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
    """Create an Options instance with a dynamic instance key."""

    return cls(
      instance_key=_generate_instance_key(project_name),
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
    return _state


def set_state(options: Options) -> None:
  """Set the global state in a thread-safe manner."""

  global _state
  with _state_lock:
    _state = options
