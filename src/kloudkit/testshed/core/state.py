import os
import random
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
class ShedState:
  instance_key: str
  image: str
  tag: str
  src_path: Path
  tests_path: Path
  stubs_path: Path

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
    project_name: str,
    image: str,
    tag: str,
    src_path: Path,
    tests_path: Path,
    stubs_path: Path,
  ) -> "ShedState":
    """Create a ShedState instance with a dynamic instance key."""

    return cls(
      instance_key=_generate_instance_key(project_name),
      image=image,
      tag=tag,
      src_path=src_path,
      tests_path=tests_path,
      stubs_path=stubs_path,
    )
