from kloudkit.testshed._internal.state import get_state

import pytest


@pytest.fixture(scope="session")
def shed_tag(request) -> str:
  """Fully-qualified Docker testing image for test runs."""

  return get_state().image_and_tag


__all__ = ["shed_tag"]
