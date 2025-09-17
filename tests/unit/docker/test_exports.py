def test_package_exports():
  from kloudkit.testshed.docker import (
    Container,
    DockerException,
    HttpProbe,
    InlineVolume,
    RemoteVolume,
    docker,
  )

  assert Container is not None
  assert DockerException is not None
  assert HttpProbe is not None
  assert InlineVolume is not None
  assert RemoteVolume is not None
  assert docker is not None
