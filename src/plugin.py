from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.bootstrap import init_shed_image, init_shed_network
from kloudkit.testshed.docker.cleanup import Cleanup

import pytest


pytest_plugins = ["kloudkit.testshed.fixtures"]


def pytest_addoption(parser) -> None:
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


def pytest_configure(config: pytest.Config) -> None:
  """Bootstrap Docker image and network used in tests."""

  state = get_state()

  state.network = config.getoption("shed_network")
  state.image = config.getoption("shed_image")
  state.tag = config.getoption("shed_tag")

  init_shed_network(state.network)

  init_shed_image(
    state.image_and_tag,
    force_build=config.getoption("shed_rebuild"),
    require_local_image=config.getoption("shed_require_image"),
    context_path=config.rootpath,
  )


def pytest_keyboard_interrupt(excinfo: pytest.ExceptionInfo) -> None:
  """Cleanup any dangling containers before exiting."""

  Cleanup.run()
