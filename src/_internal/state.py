from dataclasses import dataclass, field


@dataclass(slots=True)
class Options:
  labels: dict[str, str] = field(
    default_factory=lambda: {"com.kloudkit.testshed": "testing-container"}
  )
  network: str = "testshed-network"
  image: str | None = None
  tag: str = "tests"
  stubs_dir: str = "stubs"

  @property
  def image_and_tag(self) -> str:
    """Fully-qualified Docker testing image for test runs."""

    sep = ":"

    if self.tag.startswith("sha"):
      sep = "@"

    return f"{self.image}{sep}{self.tag}"


_state: Options = Options()


def get_state() -> Options:
  """Get the current state."""

  return _state
