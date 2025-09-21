from kloudkit.testshed.docker.volumes.base_volume import BaseVolume

import pytest


def shed_config(**configs) -> pytest.MarkDecorator:
  """Assign generic configs to the `shed` instance."""

  return pytest.mark.shed_config(**configs)


def shed_env(**envs) -> pytest.MarkDecorator:
  """Assign environment variables to the `shed` instance."""

  return pytest.mark.shed_env(**envs)


def shed_volumes(*mounts: tuple[str, str] | BaseVolume) -> pytest.MarkDecorator:
  """Assign volume mounts to the `shed` instance."""

  return pytest.mark.shed_volumes(*mounts)


def shed_mutable() -> pytest.MarkDecorator:
  """Force non-default shed for tests that perform mutable operations."""

  return pytest.mark.shed_env(_SHED_MUTABLE="true")
