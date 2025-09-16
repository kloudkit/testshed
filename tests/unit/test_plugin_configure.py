from unittest.mock import Mock

from kloudkit.testshed.plugin.validation import validate_config

import pytest


def _create_config_mock(shed_image=None, shed_image_policy=None):
  config = Mock(spec=pytest.Config)

  config.getoption.side_effect = lambda option: {
    "shed_image": shed_image,
    "shed_image_policy": shed_image_policy,
  }[option]

  return config


@pytest.mark.parametrize("shed_image", [None, ""])
def test_missing_shed_image(shed_image):
  config = _create_config_mock(shed_image=shed_image, shed_image_policy="pull")

  with pytest.raises(
    pytest.UsageError, match="TestShed requires --shed-image to be specified"
  ):
    validate_config(config)


@pytest.mark.parametrize("shed_image_policy", ["invalid", "wrong", None, ""])
def test_invalid_shed_policy(shed_image_policy):
  config = _create_config_mock(
    shed_image="my-test-image", shed_image_policy=shed_image_policy
  )

  with pytest.raises(pytest.UsageError, match="Invalid --shed-image-policy"):
    validate_config(config)


@pytest.mark.parametrize(
  "shed_image_policy", ["pull", "build", "require", "rebuild"]
)
def test_valid_config(shed_image_policy):
  config = _create_config_mock(
    shed_image="my-test-image", shed_image_policy=shed_image_policy
  )

  validate_config(config)
