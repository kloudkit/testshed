from kloudkit.testshed.docker import Container, docker

import pytest


_EXTERNAL_NAME = "testshed-attach-external"


@pytest.fixture
def external_container(shed_tag):
  """Stand-in for a container owned outside the test run."""

  docker.container.remove(_EXTERNAL_NAME, force=True)

  container = docker.run(
    shed_tag,
    ["sleep", "infinity"],
    name=_EXTERNAL_NAME,
    detach=True,
    remove=False,
  )

  yield container

  docker.container.remove(container, force=True)


def test_attach_exposes_shed_methods(external_container, shed_attach):
  attached = shed_attach(external_container.name)

  assert isinstance(attached, Container)
  assert attached.execute(["echo", "hi"]) == "hi"
  assert attached.fs.exists("/")
  assert attached.whoami() == "root"


def test_attach_joins_shed_network(external_container, shed_attach, shed_state):
  attached = shed_attach(external_container.name)

  networks = attached.wrapped.network_settings.networks

  assert shed_state.network in networks


def test_attach_can_reach_managed_container(
  external_container, shed_attach, shed_default
):
  attached = shed_attach(external_container.name)

  assert attached.execute(["getent", "hosts", shed_default.name])


def test_attach_does_not_own_the_container(external_container, shed_attach):
  shed_attach(external_container.name)

  # The stand-in carries no testshed labels, so plugin cleanup never targets it.
  assert "com.kloudkit.testshed" not in (external_container.config.labels or {})
  assert docker.container.exists(external_container.name)
