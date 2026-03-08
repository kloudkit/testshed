from unittest.mock import Mock

from kloudkit.testshed.docker.container_config import ContainerConfig

import pytest


def test_default_values():
  config = ContainerConfig(
    envs={}, volumes=(), args={}, test_name="test_example"
  )

  assert config.envs == {}
  assert config.volumes == ()
  assert config.args == {}
  assert config.test_name == "test_example"


@pytest.mark.parametrize(
  ("envs", "volumes", "args", "expected"),
  [
    ({}, (), {}, False),
    ({"KEY": "value"}, (), {}, True),
    ({}, ("/path/to/volume",), {}, True),
    ({}, (), {"key": "value"}, True),
  ],
)
def test_has_overrides(envs, volumes, args, expected):
  config = ContainerConfig(
    envs=envs, volumes=volumes, args=args, test_name="test_example"
  )

  assert config.has_overrides == expected


def test_to_dict():
  config = ContainerConfig(
    envs={"ENV_VAR": "value"},
    volumes=("/vol1", "/vol2"),
    args={"arg1": "val1", "arg2": "val2"},
    test_name="test_example",
  )

  result = config.to_dict()

  assert result == {
    "envs": {"ENV_VAR": "value"},
    "volumes": ("/vol1", "/vol2"),
    "test_name": "test_example",
    "arg1": "val1",
    "arg2": "val2",
  }


def test_create_with_no_markers():
  request = Mock()
  request.node.get_closest_marker.return_value = None
  request.node.nodeid = "test_module::test_function"

  config = ContainerConfig.create(request)

  assert config.envs == {}
  assert config.volumes == ()
  assert config.args == {}
  assert config.test_name == "test_module::test_function"


def test_create_with_all_markers():
  request = Mock()
  request.node.nodeid = "test_module::test_function"

  markers = {
    "shed_env": Mock(kwargs={"ENV": "value"}),
    "shed_volumes": Mock(args=("/vol1",)),
    "shed_config": Mock(kwargs={"image": "test:latest"}),
  }

  request.node.get_closest_marker.side_effect = markers.get

  config = ContainerConfig.create(request)

  assert config.envs == {"ENV": "value"}
  assert config.volumes == ("/vol1",)
  assert config.args == {"image": "test:latest"}
  assert config.test_name == "test_module::test_function"


def test_merge_with_no_overrides():
  config = ContainerConfig(
    envs={"A": "1"}, volumes=("/v1",), args={"x": "y"}, test_name="test_fn"
  )

  merged = config.merge()

  assert merged.envs == {"A": "1"}
  assert merged.volumes == ("/v1",)
  assert merged.args == {"x": "y"}
  assert merged.test_name == "test_fn"


def test_merge_envs_override_and_add():
  config = ContainerConfig(
    envs={"A": "1", "B": "2"}, volumes=(), args={}, test_name="test_fn"
  )

  merged = config.merge(envs={"B": "overridden", "C": "3"})

  assert merged.envs == {"A": "1", "B": "overridden", "C": "3"}


def test_merge_volumes_concatenate():
  config = ContainerConfig(
    envs={}, volumes=("/v1",), args={}, test_name="test_fn"
  )

  merged = config.merge(volumes=("/v2", "/v3"))

  assert merged.volumes == ("/v1", "/v2", "/v3")


def test_merge_args_override():
  config = ContainerConfig(
    envs={}, volumes=(), args={"a": "1", "b": "2"}, test_name="test_fn"
  )

  merged = config.merge(args={"b": "overridden", "c": "3"})

  assert merged.args == {"a": "1", "b": "overridden", "c": "3"}


def test_merge_preserves_test_name():
  config = ContainerConfig(
    envs={}, volumes=(), args={}, test_name="original::test"
  )

  merged = config.merge(envs={"X": "1"})

  assert merged.test_name == "original::test"
