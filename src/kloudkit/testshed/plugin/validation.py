import pytest


def _raise(message: str):
  raise pytest.UsageError(message)


def validate_config(config: pytest.Config) -> None:
  """Validate required pytest configuration options."""

  if config.inipath is None:
    _raise("TestShed needs a pytest config file to resolve its paths from")

  shed_image = config.getoption("shed_image")

  if not shed_image:
    _raise(
      "TestShed requires --shed-image to be specified when --shed is enabled"
    )

  if "@" in shed_image or ":" in shed_image.rsplit("/", 1)[-1]:
    _raise(
      f"--shed-image [{shed_image}] must not contain a tag or digest."
      " Pass the tag via --shed-tag instead"
      " (e.g. --shed-image=ghcr.io/kloudkit/app --shed-tag=pr-563)"
    )
