import contextlib

from python_on_whales import docker
from python_on_whales.exceptions import DockerException

from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.docker.container import Container

import pytest


def _disconnect(network: str, container) -> None:
  """Detach a container from the shed network, ignoring failures."""

  with contextlib.suppress(DockerException):
    docker.network.disconnect(network, container)


def _make_attach(request, state: ShedState, container_class):
  """Build the attach callable returned by `shed_attach`."""

  network = state.network

  def _attach(name_or_id: str) -> Container:
    container = container_class.attach(
      name_or_id, container_logs=bool(state.container_logs)
    )

    networks = container.wrapped.network_settings.networks or {}

    if network not in networks:
      docker.network.connect(network, container.wrapped)

      request.addfinalizer(lambda: _disconnect(network, container.wrapped))

    return container

  return _attach


@pytest.fixture
def shed_attach(request, shed_state: ShedState, shed_container_defaults):
  """Attach existing, externally-managed containers to the shed network."""

  return _make_attach(
    request,
    shed_state,
    shed_container_defaults.get("container_class", Container),
  )
