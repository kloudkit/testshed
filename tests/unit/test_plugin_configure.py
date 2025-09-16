from unittest.mock import Mock

from kloudkit.testshed.plugin.validation import validate_config

import pytest


@pytest.mark.parametrize("shed_image", [None, ""])
def test_raises_usage_error_when_shed_image_missing(shed_image):
  config = Mock(spec=pytest.Config)
  config.getoption.return_value = shed_image

  with pytest.raises(
    pytest.UsageError, match="TestShed requires --shed-image to be specified"
  ):
    validate_config(config)


def test_passes_when_shed_image_provided():
  config = Mock(spec=pytest.Config)
  config.getoption.return_value = "my-test-image"

  validate_config(config)
