from typing import Generator

from kloudkit.testshed.docker import Factory

import pytest


def _create_docker_sidecar() -> Generator[Factory, None, None]:
  """Launch Docker sidecar instances."""

  factory = Factory()

  yield factory

  factory.cleanup()


@pytest.fixture
def docker_sidecar() -> Generator[Factory, None, None]:
  """Function-scoped Docker sidecar."""

  yield from _create_docker_sidecar()


@pytest.fixture(scope="module")
def docker_module_sidecar() -> Generator[Factory, None, None]:
  """Module-scoped Docker sidecar."""

  yield from _create_docker_sidecar()


@pytest.fixture(scope="session")
def docker_session_sidecar() -> Generator[Factory, None, None]:
  """Session-scoped Docker sidecar."""

  yield from _create_docker_sidecar()
