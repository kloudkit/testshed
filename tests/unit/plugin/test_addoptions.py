from unittest.mock import Mock

from kloudkit.testshed.plugin.addoptions import pytest_addoption

import pytest


def test_all_options_registered():
  parser = Mock(spec=pytest.Parser)

  pytest_addoption(parser)

  assert parser.addoption.call_count == 10

  option_names = [c.args[0] for c in parser.addoption.call_args_list]

  assert option_names == [
    "--shed",
    "--shed-image",
    "--shed-tag",
    "--shed-build-context",
    "--shed-image-policy",
    "--shed-src-dir",
    "--shed-stubs-dir",
    "--shed-tests-dir",
    "--shed-skip-bootstrap",
    "--shed-container-logs",
  ]


def test_shed_option_defaults():
  parser = Mock(spec=pytest.Parser)

  pytest_addoption(parser)

  calls = {c.args[0]: c.kwargs for c in parser.addoption.call_args_list}

  assert calls["--shed"]["default"] is False
  assert calls["--shed"]["action"] == "store_true"


def test_shed_tag_default():
  parser = Mock(spec=pytest.Parser)

  pytest_addoption(parser)

  calls = {c.args[0]: c.kwargs for c in parser.addoption.call_args_list}

  assert calls["--shed-tag"]["default"] == "tests"


def test_shed_image_policy_choices():
  parser = Mock(spec=pytest.Parser)

  pytest_addoption(parser)

  calls = {c.args[0]: c.kwargs for c in parser.addoption.call_args_list}

  assert calls["--shed-image-policy"]["choices"] == [
    "pull",
    "build",
    "require",
    "rebuild",
  ]
  assert calls["--shed-image-policy"]["default"] == "pull"


def test_shed_dir_defaults():
  parser = Mock(spec=pytest.Parser)

  pytest_addoption(parser)

  calls = {c.args[0]: c.kwargs for c in parser.addoption.call_args_list}

  assert calls["--shed-src-dir"]["default"] == "src"
  assert calls["--shed-stubs-dir"]["default"] == "tests/stubs"
  assert calls["--shed-tests-dir"]["default"] == "tests"


def test_boolean_options_are_store_true():
  parser = Mock(spec=pytest.Parser)

  pytest_addoption(parser)

  calls = {c.args[0]: c.kwargs for c in parser.addoption.call_args_list}

  assert calls["--shed-skip-bootstrap"]["action"] == "store_true"
  assert calls["--shed-container-logs"]["action"] == "store_true"
