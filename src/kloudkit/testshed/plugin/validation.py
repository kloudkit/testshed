import pytest


def _raise(message: str):
  raise pytest.UsageError(message)


def validate_config(config: pytest.Config) -> None:
  """Validate required pytest configuration options."""

  shed_image = config.getoption("shed_image")
  shed_image_policy = config.getoption("shed_image_policy")
  shed_playwright_image = config.getoption("shed_playwright_image")

  if not shed_image:
    _raise(
      "TestShed requires --shed-image to be specified when --shed is enabled"
    )

  if ":" in shed_image or "@" in shed_image:
    _raise(
      f"--shed-image [{shed_image}] must not contain a tag or digest."
      " Pass the tag via --shed-tag instead"
      " (e.g. --shed-image=ghcr.io/kloudkit/app --shed-tag=pr-563)"
    )

  if ":" in shed_playwright_image or "@" in shed_playwright_image:
    _raise(
      f"--shed-playwright-image [{shed_playwright_image}] must not contain"
      " a tag or digest. Its tag is the installed playwright version"
      " (e.g. --shed-playwright-image=mirror.example/playwright)"
    )

  if shed_image_policy not in ["pull", "build", "require", "rebuild"]:
    _raise(
      f"Invalid --shed-image-policy [{shed_image_policy}]."
      " Must be one of: pull, build, require, rebuild"
    )
