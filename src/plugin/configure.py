from pathlib import Path

from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.bootstrap import init_shed_image, init_shed_network

import pytest


def _resolve_path(directory: str, config: pytest.Config) -> Path:
  directory = config.getoption(f"shed_{directory}")

  return (config.inipath.parent / directory).resolve()


def pytest_configure(config: pytest.Config) -> None:
  """Bootstrap Docker image and network used in tests."""

  state = get_state()

  state.network = config.getoption("shed_network")
  state.image = config.getoption("shed_image")
  state.tag = config.getoption("shed_tag")

  state.src_path = _resolve_path("src_dir", config)
  state.stubs_path = _resolve_path("stubs_dir", config)
  state.tests_path = _resolve_path("tests_dir", config)

  context_path = (
    config.getoption("shed_docker_context") or config.inipath.parent
  )

  init_shed_network(state.network)

  init_shed_image(
    state.image_and_tag,
    force_build=config.getoption("shed_rebuild"),
    require_local_image=config.getoption("shed_require_image"),
    context_path=context_path,
  )
