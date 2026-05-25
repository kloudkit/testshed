from unittest.mock import MagicMock, Mock

from kloudkit.testshed.docker.container_config import ContainerConfig
from kloudkit.testshed.fixtures.shed import _make_deferred_deploy

import pytest


def _config(envs=None, volumes=(), args=None, test_name="test_fn"):
  return ContainerConfig(
    envs=envs or {},
    volumes=volumes,
    args=args or {},
    test_name=test_name,
  )


@pytest.fixture
def factory():
  return MagicMock(return_value="container")


def test_deferred_no_decorators_no_params(factory):
  deploy = _make_deferred_deploy(_config(), factory)

  result = deploy()

  assert result == "container"
  factory.assert_called_once_with(envs={}, volumes=(), test_name="test_fn")


def test_deferred_with_decorator_config(factory):
  deploy = _make_deferred_deploy(
    _config(envs={"DB": "postgres"}, volumes=("/data",), args={"port": "5432"}),
    factory,
  )

  result = deploy()

  assert result == "container"
  factory.assert_called_once_with(
    envs={"DB": "postgres"},
    volumes=("/data",),
    test_name="test_fn",
    port="5432",
  )


def test_deferred_call_time_overrides_supplement(factory):
  deploy = _make_deferred_deploy(
    _config(envs={"A": "1"}, volumes=("/v1",)),
    factory,
  )

  deploy(envs={"B": "2"}, volumes=("/v2",))

  factory.assert_called_once_with(
    envs={"A": "1", "B": "2"},
    volumes=("/v1", "/v2"),
    test_name="test_fn",
  )


def test_deferred_call_time_overrides_replace(factory):
  deploy = _make_deferred_deploy(
    _config(envs={"A": "1", "B": "original"}, args={"x": "old"}),
    factory,
  )

  deploy(envs={"B": "replaced"}, x="new")

  factory.assert_called_once_with(
    envs={"A": "1", "B": "replaced"},
    volumes=(),
    test_name="test_fn",
    x="new",
  )


def test_deferred_envs_override_from_decorator_and_add_new(factory):
  deploy = _make_deferred_deploy(
    _config(envs={"EXISTING": "original", "KEEP": "same"}),
    factory,
  )

  deploy(envs={"EXISTING": "overridden", "NEW_VAR": "added"})

  factory.assert_called_once_with(
    envs={"EXISTING": "overridden", "KEEP": "same", "NEW_VAR": "added"},
    volumes=(),
    test_name="test_fn",
  )


def test_deferred_multiple_calls(factory):
  factory.side_effect = ["container1", "container2"]
  deploy = _make_deferred_deploy(_config(), factory)

  r1 = deploy(envs={"A": "1"})
  r2 = deploy(envs={"B": "2"})

  assert r1 == "container1"
  assert r2 == "container2"
  assert factory.call_count == 2


def test_deferred_picks_up_markers_via_container_config(factory):
  request = Mock(spec=pytest.FixtureRequest)
  request.node.nodeid = "module::test_fn"
  request.node.get_closest_marker.side_effect = {
    "shed_env": Mock(kwargs={"DEBUG": "true"}),
    "shed_volumes": Mock(args=(("host", "/in/container"),)),
    "shed_config": Mock(kwargs={"workdir": "/tmp"}),
  }.get

  deploy = _make_deferred_deploy(ContainerConfig.create(request), factory)
  deploy()

  factory.assert_called_once_with(
    envs={"DEBUG": "true"},
    volumes=(("host", "/in/container"),),
    test_name="module::test_fn",
    workdir="/tmp",
  )
