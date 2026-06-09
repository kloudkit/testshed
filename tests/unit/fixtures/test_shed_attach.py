from types import SimpleNamespace
from unittest.mock import Mock, patch

from kloudkit.testshed.fixtures.shed import _make_attach

import pytest


def _state(network="testshed-net", container_logs=None):
  return SimpleNamespace(network=network, container_logs=container_logs)


def _container(networks=None):
  wrapped = SimpleNamespace(
    network_settings=SimpleNamespace(networks=networks or {}),
    remove=Mock(),
  )

  return SimpleNamespace(wrapped=wrapped)


def test_attach_connects_to_network_and_registers_finalizer():
  request = Mock(spec=pytest.FixtureRequest)
  state = _state()
  container = _container()
  container_class = Mock(attach=Mock(return_value=container))

  with patch("kloudkit.testshed.fixtures.shed.docker") as docker:
    attach = _make_attach(request, state, container_class)
    result = attach("my-container")

  assert result is container
  container_class.attach.assert_called_once_with(
    "my-container", container_logs=False
  )
  docker.network.connect.assert_called_once_with(
    "testshed-net", container.wrapped
  )
  request.addfinalizer.assert_called_once()


def test_attach_finalizer_disconnects_and_never_removes():
  request = Mock(spec=pytest.FixtureRequest)
  state = _state()
  container = _container()
  container_class = Mock(attach=Mock(return_value=container))

  with patch("kloudkit.testshed.fixtures.shed.docker") as docker:
    attach = _make_attach(request, state, container_class)
    attach("my-container")

    finalizer = request.addfinalizer.call_args.args[0]
    finalizer()

  docker.network.disconnect.assert_called_once_with(
    "testshed-net", container.wrapped
  )
  container.wrapped.remove.assert_not_called()


def test_attach_skips_network_when_already_connected():
  request = Mock(spec=pytest.FixtureRequest)
  state = _state()
  container = _container(networks={"testshed-net": object()})
  container_class = Mock(attach=Mock(return_value=container))

  with patch("kloudkit.testshed.fixtures.shed.docker") as docker:
    attach = _make_attach(request, state, container_class)
    attach("my-container")

  docker.network.connect.assert_not_called()
  request.addfinalizer.assert_not_called()
