from kloudkit.testshed.docker.runtime.cleanup import Cleanup
from kloudkit.testshed.plugin.addoptions import pytest_addoption  # noqa: F401
from kloudkit.testshed.plugin.configure import pytest_configure  # noqa: F401
from kloudkit.testshed.plugin.presenter import (
  pytest_report_header,  # noqa: F401
)

import pytest


pytest_plugins = ["kloudkit.testshed.fixtures"]


def pytest_keyboard_interrupt(excinfo: pytest.ExceptionInfo) -> None:
  """Cleanup any dangling containers before exiting."""

  Cleanup.run()
