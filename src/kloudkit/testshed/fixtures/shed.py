from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.docker.container_config import ContainerConfig
from kloudkit.testshed.docker.probes.http_probe import HttpProbe

import pytest


@pytest.fixture(scope="session")
def shed_state(request: pytest.FixtureRequest) -> ShedState:
  """TestShed state configuration."""

  return request.config.shed


@pytest.fixture(scope="session")
def shed_container_defaults():
  """Container configuration defaults."""

  return {}


@pytest.fixture(scope="session")
def shed_tag(shed_state: ShedState) -> str:
  """Fully-qualified Docker testing image for test runs."""

  return shed_state.image_and_tag


@pytest.fixture(scope="session")
def shed_default(shed_tag, docker_session_sidecar, shed_container_defaults):
  """Reusable container instance with configurable defaults."""

  return docker_session_sidecar(
    image=shed_tag,
    test_name="shed_default",
    **shed_container_defaults,
  )


@pytest.fixture
def shed_factory(shed_tag, docker_sidecar, shed_container_defaults):
  """Callable factory for spinning up containers with configurable defaults."""

  def _wrapper(**kwargs):
    port = kwargs.pop("port", None)
    user_probe = kwargs.pop("probe", ...)

    probe = shed_container_defaults.get("probe")

    if port is not None and probe:
      probe = probe.merge(HttpProbe(port=port))

    if user_probe is not ...:
      probe = probe.merge(user_probe) if (probe and user_probe) else user_probe

    merged_config = {**shed_container_defaults, **kwargs}
    if probe:
      merged_config["probe"] = probe

    return docker_sidecar(image=shed_tag, **merged_config)

  return _wrapper


@pytest.fixture
def shed_deferred(request: pytest.FixtureRequest):
  """Callable that deploys a container when invoked."""

  config = ContainerConfig.create(request)
  shed_factory = request.getfixturevalue("shed_factory")

  def _deploy(*, envs=None, volumes=None, **kwargs):
    return shed_factory(
      **config.merge(envs=envs, volumes=volumes, args=kwargs).to_dict()
    )

  return _deploy


@pytest.fixture
def shed(request: pytest.FixtureRequest):
  """Reuses default or creates new based on markers."""

  config = ContainerConfig.create(request)

  if not config.has_overrides:
    return request.getfixturevalue("shed_default")

  shed_factory = request.getfixturevalue("shed_factory")

  return shed_factory(**config.to_dict())
