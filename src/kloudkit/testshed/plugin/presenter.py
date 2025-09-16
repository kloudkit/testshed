from kloudkit.testshed._internal.state import get_state

import pytest


def pytest_report_header(config: pytest.Config) -> list[str]:
  """Append to the test headers."""

  if not config.getoption("shed"):
    return []

  if config.getoption("shed_skip_bootstrap"):
    return ["shed-bootstrap: skipped"]

  state = get_state()

  return [
    f"shed-image: {state.image_and_tag}",
    f"shed-network: {state.network}",
    f"shed-stubs: {state.stubs_path}",
  ]
