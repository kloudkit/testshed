from kloudkit.testshed.docker.runtime.cleanup import Cleanup

import pytest


def pytest_sessionfinish(session: pytest.Session):
  """Cleanup all Docker resources at the end of the test session."""

  Cleanup(session.config.shed).run(network=True)
