from unittest.mock import Mock

from kloudkit.testshed.plugin.markers import register

import pytest


def test_register_adds_all_markers():
  config = Mock(spec=pytest.Config)

  register(config)

  assert config.addinivalue_line.call_count == 4


def test_register_marker_names():
  config = Mock(spec=pytest.Config)

  register(config)

  marker_lines = [c.args[1] for c in config.addinivalue_line.call_args_list]

  assert any("shed_config" in m for m in marker_lines)
  assert any("shed_env" in m for m in marker_lines)
  assert any("shed_volumes" in m for m in marker_lines)
  assert any("shed_mutable" in m for m in marker_lines)


def test_register_uses_markers_category():
  config = Mock(spec=pytest.Config)

  register(config)

  for c in config.addinivalue_line.call_args_list:
    assert c.args[0] == "markers"
