from pathlib import Path

from kloudkit.testshed.core.bootstrap import init_shed_image, init_shed_network
from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.plugin.fixtures import register as register_fixtures
from kloudkit.testshed.plugin.markers import register as register_markers
from kloudkit.testshed.plugin.validation import validate_config

import pytest


def _resolve_path(directory: str, config: pytest.Config) -> Path:
  directory = config.getoption(f"shed_{directory}")

  return (config.inipath.parent / directory).resolve()


def pytest_configure(config: pytest.Config) -> None:
  """Bootstrap Docker image and network used in tests."""

  if not config.getoption("shed"):
    return

  validate_config(config)
  register_markers(config)
  register_fixtures(config)

  state = ShedState.create(
    project_name=config.inipath.parent.name,
    image=config.getoption("shed_image"),
    tag=config.getoption("shed_tag"),
    src_path=_resolve_path("src_dir", config),
    stubs_path=_resolve_path("stubs_dir", config),
    tests_path=_resolve_path("tests_dir", config),
  )

  config.shed = state

  if config.getoption("shed_skip_bootstrap"):
    return

  context_path = config.getoption("shed_build_context") or config.inipath.parent

  init_shed_network(state.network)

  init_shed_image(
    state.image_and_tag,
    policy=config.getoption("shed_image_policy"),
    context_path=context_path,
  )
