import pytest


def pytest_report_header(config: pytest.Config) -> list[str]:
  """Append to the test headers."""

  if not config.getoption("shed"):
    return []

  if config.getoption("shed_skip_bootstrap"):
    return ["shed-bootstrap: skipped"]

  container_logs = "active" if config.shed.container_logs else "skipped"

  return [
    f"shed-image: {config.shed.image_and_tag}",
    f"shed-network: {config.shed.network}",
    f"shed-stubs: {config.shed.stubs_path}",
    f"shed-container-logs: {container_logs}",
  ]
