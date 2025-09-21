from unittest.mock import Mock

from kloudkit.testshed.plugin.presenter import pytest_report_header

import pytest


def test_header_no_shed():
  config = Mock(spec=pytest.Config)
  config.getoption.return_value = False

  assert pytest_report_header(config) == []


def test_header_skip_bootstrap():
  config = Mock(spec=pytest.Config)

  config.getoption.side_effect = lambda option: {
    "shed": True,
    "shed_skip_bootstrap": True,
  }[option]

  assert pytest_report_header(config) == ["shed-bootstrap: skipped"]


def test_header_with_shed():
  config = Mock(spec=pytest.Config)

  config.getoption.side_effect = lambda option: {
    "shed": True,
    "shed_skip_bootstrap": False,
  }[option]

  shed_mock = Mock()
  shed_mock.image_and_tag = "test-image:latest"
  shed_mock.network = "test-network"
  shed_mock.stubs_path = "/path/to/stubs"
  config.shed = shed_mock

  assert pytest_report_header(config) == [
    "shed-image: test-image:latest",
    "shed-network: test-network",
    "shed-stubs: /path/to/stubs",
  ]
