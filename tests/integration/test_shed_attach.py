from kloudkit.testshed.docker import docker

import pytest


@pytest.fixture
def external_container(shed_tag):
  docker.container.remove("testshed-attach-external", force=True)

  container = docker.run(
    shed_tag,
    ["sleep", "infinity"],
    name="testshed-attach-external",
    detach=True,
  )

  yield container

  docker.container.remove(container, force=True)


def test_attach_exposes_shed_methods(external_container, shed_attach):
  attached = shed_attach(external_container.name)

  assert attached.execute(["echo", "hi"]) == "hi"
  assert attached.whoami() == "root"


def test_attach_joins_shed_network(external_container, shed_attach, shed_state):
  attached = shed_attach(external_container.name)

  assert shed_state.network in attached.wrapped.network_settings.networks


def test_attach_reaches_managed_container(
  external_container, shed_attach, shed_default
):
  attached = shed_attach(external_container.name)

  assert attached.execute(["getent", "hosts", shed_default.name])
