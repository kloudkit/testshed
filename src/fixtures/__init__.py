from pathlib import Path

from kloudkit.testshed._internal.state import get_state

import pytest


@pytest.fixture(scope="session")
def test_root() -> Path:
  """Absolute path to the tests root."""

  return get_state().tests_path


@pytest.fixture(scope="session")
def project_root() -> Path:
  """Absolute path to the project source root."""

  return get_state().src_path


@pytest.fixture(scope="session")
def shed_tag(request: pytest.FixtureRequest) -> str:
  """Fully-qualified Docker testing image for test runs."""

  return get_state().image_and_tag


__all__ = ["shed_tag"]
