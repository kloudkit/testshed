from types import SimpleNamespace
from unittest.mock import Mock, patch

from kloudkit.testshed.fixtures.attach import _make_attach

import pytest


def _container(networks=None):
  wrapped = SimpleNamespace(
    network_settings=SimpleNamespace(networks=networks or {}),
    remove=Mock(),
  )

  return SimpleNamespace(wrapped=wrapped)


@pytest.fixture
def request_mock():
  return Mock(spec=pytest.FixtureRequest)


@pytest.fixture
def state():
  return SimpleNamespace(network="shed-net", container_logs=None)


def test_attach_connects_then_finalizer_disconnects(request_mock, state):
  container = _container()
  wrapped = container.wrapped
  container_class = Mock(attach=Mock(return_value=container))

  with patch("kloudkit.testshed.fixtures.attach.docker") as docker:
    _make_attach(request_mock, state, container_class)("svc")

    docker.network.connect.assert_called_once_with("shed-net", wrapped)

    request_mock.addfinalizer.call_args.args[0]()

  docker.network.disconnect.assert_called_once_with("shed-net", wrapped)
  wrapped.remove.assert_not_called()


def test_attach_skips_when_already_connected(request_mock, state):
  container = _container(networks={"shed-net": object()})
  container_class = Mock(attach=Mock(return_value=container))

  with patch("kloudkit.testshed.fixtures.attach.docker") as docker:
    _make_attach(request_mock, state, container_class)("svc")

  docker.network.connect.assert_not_called()
  request_mock.addfinalizer.assert_not_called()


def test_attach_passes_the_log_printer(request_mock, state):
  state.container_logs = Mock()
  container_class = Mock(
    attach=Mock(return_value=_container(networks={"shed-net": object()}))
  )

  with patch("kloudkit.testshed.fixtures.attach.docker"):
    _make_attach(request_mock, state, container_class)("svc")

  container_class.attach.assert_called_once_with(
    "svc", container_logs=state.container_logs
  )
