import pytest


def _raise(message: str):
  raise pytest.UsageError(message)


def validate_config(config: pytest.Config) -> None:
  """Validate required pytest configuration options."""

  shed_image = config.getoption("shed_image")
  shed_image_policy = config.getoption("shed_image_policy")

  if not shed_image:
    _raise(
      "TestShed requires --shed-image to be specified when --shed is enabled"
    )

  if shed_image_policy not in ["pull", "build", "require", "rebuild"]:
    _raise(
      f"Invalid --shed-image-policy [{shed_image_policy}]."
      " Must be one of: pull, build, require, rebuild"
    )
