from dataclasses import dataclass
from typing import Self

import pytest


@dataclass(frozen=True, slots=True)
class ContainerConfig:
  envs: dict[str, str]
  volumes: tuple[str, ...]
  args: dict[str, str]
  test_name: str

  @property
  def has_overrides(self) -> bool:
    """If any fields are non-empty."""

    return bool(self.envs or self.volumes or self.args)

  def to_dict(self) -> dict:
    """Return a plain dict with merged configs."""

    return dict(
      envs=self.envs,
      volumes=self.volumes,
      test_name=self.test_name,
      **self.args,
    )

  @classmethod
  def create(cls, request: pytest.FixtureRequest) -> Self:
    """Create configs from a pytest request of the current node."""

    item = request.node

    config_marker = item.get_closest_marker("shed_config")
    env_marker = item.get_closest_marker("shed_env")
    volumes_marker = item.get_closest_marker("shed_volumes")

    return cls(
      envs=env_marker.kwargs if env_marker else {},
      volumes=tuple(volumes_marker.args) if volumes_marker else tuple(),
      test_name=item.nodeid,
      args=(config_marker.kwargs if config_marker else {}),
    )
