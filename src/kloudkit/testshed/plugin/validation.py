import pytest


def validate_config(config: pytest.Config) -> None:
  """Validate required pytest configuration options."""

  shed_image = config.getoption("shed_image")

  if not shed_image:
    raise pytest.UsageError(
      "TestShed requires --shed-image to be specified when --shed is enabled"
    )
