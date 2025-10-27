from kloudkit.testshed.docker.runtime.cleanup import Cleanup

import pytest


def pytest_keyboard_interrupt(excinfo):
  """Handle Ctrl+C interruption during test session."""

  print(
    "\n🛑 Test session interrupted.",
    "Cleanup has started and might take a moment...",
  )


def pytest_sessionfinish(session: pytest.Session):
  """Cleanup all Docker resources at the end of the test session."""

  if getattr(session.config, "shed", None):
    Cleanup(session.config.shed).run(network=True)
