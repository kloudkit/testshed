from kloudkit.testshed.docker.inline_volume import InlineVolume

import pytest


def shed_config(**configs) -> pytest.MarkDecorator:
  """Assign generic configs to the `shed` instance."""

  return pytest.mark.shed_config(**configs)


def shed_env(**envs) -> pytest.MarkDecorator:
  """Assign environment variables to the `shed` instance."""

  return pytest.mark.shed_env(**envs)


def shed_volumes(
  *mounts: tuple[str, str] | InlineVolume,
) -> pytest.MarkDecorator:
  """Assign volume mounts to the `shed` instance."""

  return pytest.mark.shed_volumes(*mounts)
