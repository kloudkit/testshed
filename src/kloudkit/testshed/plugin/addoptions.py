import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
  """Define CLI options for TestShed."""

  parser.addoption(
    "--shed",
    action="store_true",
    default=False,
    help="Enable TestShed for the current test suite.",
  )

  parser.addoption(
    "--shed-image",
    action="store",
    default=None,
    metavar="IMAGE",
    help="Docker image repository/name to use (e.g. ghcr.io/acme/app)",
  )

  parser.addoption(
    "--shed-tag",
    action="store",
    default="tests",
    metavar="TAG|SHA",
    help="Image tag or digest (use a SHA for immutable builds).",
  )

  parser.addoption(
    "--shed-build-context",
    action="store",
    default=None,
    metavar="DIR",
    help="Docker build context directory (defaults to the project root).",
  )

  parser.addoption(
    "--shed-image-policy",
    action="store",
    choices=["pull", "build", "require", "rebuild"],
    default="pull",
    metavar="POLICY",
    help="Image acquisition policy for building or pulling.",
  )


  parser.addoption(
    "--shed-src-dir",
    action="store",
    default="src",
    metavar="DIR",
    help="Source directory (relative to pytest.ini).",
  )

  parser.addoption(
    "--shed-stubs-dir",
    action="store",
    default="tests/stubs",
    metavar="DIR",
    help="Directory for test stubs (relative to pytest.ini).",
  )

  parser.addoption(
    "--shed-tests-dir",
    action="store",
    default="tests",
    metavar="DIR",
    help="Tests root directory (relative to pytest.ini).",
  )

  parser.addoption(
    "--shed-skip-bootstrap",
    action="store_true",
    default=False,
    help="Skip Docker bootstrapping (useful for unit tests).",
  )
