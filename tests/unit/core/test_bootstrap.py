from pathlib import Path
from unittest.mock import patch

from kloudkit.testshed.core import bootstrap


@patch("kloudkit.testshed.core.bootstrap.docker")
def test_build_passes_custom_dockerfile(docker):
  docker.image.exists.return_value = False

  bootstrap.init_shed_image(
    "img:tag",
    policy="build",
    context_path=Path("/ctx"),
    dockerfile="test.dockerfile",
  )

  assert docker.build.call_args.kwargs["file"] == Path("/ctx/test.dockerfile")


@patch("kloudkit.testshed.core.bootstrap.docker")
def test_build_defaults_to_dockerfile(docker):
  docker.image.exists.return_value = False

  bootstrap.init_shed_image(
    "img:tag", policy="build", context_path=Path("/ctx")
  )

  assert docker.build.call_args.kwargs["file"] == Path("/ctx/Dockerfile")


@patch("kloudkit.testshed.core.bootstrap.docker")
def test_rebuild_forwards_dockerfile(docker):
  docker.image.exists.return_value = True

  bootstrap.init_shed_image(
    "img:tag",
    policy="rebuild",
    context_path=Path("/ctx"),
    dockerfile="test.dockerfile",
  )

  assert docker.build.call_args.kwargs["file"] == Path("/ctx/test.dockerfile")
