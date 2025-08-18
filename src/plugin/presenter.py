from kloudkit.testshed._internal.state import get_state

import pytest


def pytest_report_header(config: pytest.Config) -> list[str]:
  """Append to the test headers."""

  return [
    f"shed-image: {get_state().image_and_tag}",
    f"shed-network: {get_state().network}",
    f"shed-stubs: {get_state().stubs_path}",
  ]
