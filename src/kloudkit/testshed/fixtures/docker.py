from typing import Generator

from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.docker.factory import Factory

import pytest


def _create_docker_sidecar(state: ShedState) -> Generator[Factory, None, None]:
  """Launch Docker sidecar instances."""

  factory = Factory(state)

  yield factory

  factory.cleanup()


@pytest.fixture
def docker_sidecar(shed_state: ShedState) -> Generator[Factory, None, None]:
  """Function-scoped Docker sidecar."""

  yield from _create_docker_sidecar(shed_state)


@pytest.fixture(scope="module")
def docker_module_sidecar(
  shed_state: ShedState,
) -> Generator[Factory, None, None]:
  """Module-scoped Docker sidecar."""

  yield from _create_docker_sidecar(shed_state)


@pytest.fixture(scope="session")
def docker_session_sidecar(
  shed_state: ShedState,
) -> Generator[Factory, None, None]:
  """Session-scoped Docker sidecar."""

  yield from _create_docker_sidecar(shed_state)
