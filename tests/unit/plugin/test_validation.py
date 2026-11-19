from unittest.mock import Mock

from kloudkit.testshed.plugin.validation import validate_config

import pytest


def _create_config_mock(shed_image=None):
  config = Mock(spec=pytest.Config)

  config.getoption.side_effect = {"shed_image": shed_image}.get

  return config


@pytest.mark.parametrize("shed_image", [None, ""])
def test_missing_shed_image(shed_image):
  config = _create_config_mock(shed_image=shed_image)

  with pytest.raises(
    pytest.UsageError, match="TestShed requires --shed-image to be specified"
  ):
    validate_config(config)


@pytest.mark.parametrize(
  "shed_image",
  [
    "ghcr.io/kloudkit/workspace:pr-563",
    "debian:13",
    "myimage@sha256:abc123",
    "localhost:5000/app:tests",
    "localhost:5000/app@sha256:abc123",
  ],
)
def test_shed_image_with_tag_or_digest(shed_image):
  config = _create_config_mock(shed_image=shed_image)

  with pytest.raises(
    pytest.UsageError, match="must not contain a tag or digest"
  ):
    validate_config(config)


def test_valid_config():
  config = _create_config_mock(shed_image="my-test-image")

  validate_config(config)


def test_missing_config_file():
  config = _create_config_mock(shed_image="debian")
  config.inipath = None

  with pytest.raises(pytest.UsageError, match="pytest config file"):
    validate_config(config)


def test_shed_image_with_registry_port():
  validate_config(_create_config_mock(shed_image="localhost:5000/app"))
