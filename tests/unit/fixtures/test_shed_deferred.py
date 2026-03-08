from unittest.mock import MagicMock

from kloudkit.testshed.docker.container_config import ContainerConfig

import pytest


@pytest.fixture
def mock_shed_factory():
  return MagicMock(return_value="container")


@pytest.fixture
def make_deferred(mock_shed_factory):
  """Helper to create a deferred callable from a config."""

  def _make(config):
    def _deploy(*, envs=None, volumes=None, **kwargs):
      merged = config.merge(envs=envs, volumes=volumes, args=kwargs)
      return mock_shed_factory(**merged.to_dict())

    return _deploy

  return _make


def test_deferred_no_decorators_no_params(make_deferred, mock_shed_factory):
  config = ContainerConfig(envs={}, volumes=(), args={}, test_name="test_fn")
  deploy = make_deferred(config)

  result = deploy()

  assert result == "container"
  mock_shed_factory.assert_called_once_with(
    envs={}, volumes=(), test_name="test_fn"
  )


def test_deferred_with_decorator_config(make_deferred, mock_shed_factory):
  config = ContainerConfig(
    envs={"DB": "postgres"},
    volumes=("/data",),
    args={"port": "5432"},
    test_name="test_fn",
  )
  deploy = make_deferred(config)

  result = deploy()

  assert result == "container"
  mock_shed_factory.assert_called_once_with(
    envs={"DB": "postgres"},
    volumes=("/data",),
    test_name="test_fn",
    port="5432",
  )


def test_deferred_call_time_overrides_supplement(
  make_deferred, mock_shed_factory
):
  config = ContainerConfig(
    envs={"A": "1"}, volumes=("/v1",), args={}, test_name="test_fn"
  )
  deploy = make_deferred(config)

  deploy(envs={"B": "2"}, volumes=("/v2",))

  mock_shed_factory.assert_called_once_with(
    envs={"A": "1", "B": "2"},
    volumes=("/v1", "/v2"),
    test_name="test_fn",
  )


def test_deferred_call_time_overrides_replace(make_deferred, mock_shed_factory):
  config = ContainerConfig(
    envs={"A": "1", "B": "original"},
    volumes=(),
    args={"x": "old"},
    test_name="test_fn",
  )
  deploy = make_deferred(config)

  deploy(envs={"B": "replaced"}, x="new")

  mock_shed_factory.assert_called_once_with(
    envs={"A": "1", "B": "replaced"},
    volumes=(),
    test_name="test_fn",
    x="new",
  )


def test_deferred_envs_override_from_decorator_and_add_new(
  make_deferred, mock_shed_factory
):
  config = ContainerConfig(
    envs={"EXISTING": "original", "KEEP": "same"},
    volumes=(),
    args={},
    test_name="test_fn",
  )
  deploy = make_deferred(config)

  deploy(envs={"EXISTING": "overridden", "NEW_VAR": "added"})

  mock_shed_factory.assert_called_once_with(
    envs={"EXISTING": "overridden", "KEEP": "same", "NEW_VAR": "added"},
    volumes=(),
    test_name="test_fn",
  )


def test_deferred_multiple_calls(make_deferred, mock_shed_factory):
  mock_shed_factory.side_effect = ["container1", "container2"]
  config = ContainerConfig(envs={}, volumes=(), args={}, test_name="test_fn")
  deploy = make_deferred(config)

  r1 = deploy(envs={"A": "1"})
  r2 = deploy(envs={"B": "2"})

  assert r1 == "container1"
  assert r2 == "container2"
  assert mock_shed_factory.call_count == 2
