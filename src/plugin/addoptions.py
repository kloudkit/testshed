import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
  """Define CLI options for TestShed."""

  parser.addoption(
    "--shed-rebuild",
    action="store_true",
    default=False,
    help="Force a rebuild of the Docker testing image",
  )

  parser.addoption(
    "--shed-require-image",
    action="store_true",
    default=False,
    help="Fail if the testing image is not loaded locally",
  )

  parser.addoption(
    "--shed-image",
    default="testshed-image",
    action="store",
    help="Docker image for testing",
  )

  parser.addoption(
    "--shed-tag",
    action="store",
    default="tests",
    help="Docker tag for the testing image",
  )

  parser.addoption(
    "--shed-network",
    action="store",
    default="testshed-network",
    help="Docker network to be used when running containers",
  )

  parser.addoption(
    "--shed-docker-context",
    action="store",
    default=None,
    metavar="DIR",
    help="Docker build context (relative and defaults to the `pytest.ini`)",
  )

  parser.addoption(
    "--shed-src-dir",
    action="store",
    default="src",
    help="Source root directory (relative to the `pytest.ini`)",
  )

  parser.addoption(
    "--shed-stubs-dir",
    action="store",
    default="tests/stubs",
    metavar="DIR",
    help="Directory for test stubs (relative to the `pytest.ini`)",
  )

  parser.addoption(
    "--shed-tests-dir",
    action="store",
    default="tests",
    metavar="DIR",
    help="Tests root directory (relative to the `pytest.ini`)",
  )
