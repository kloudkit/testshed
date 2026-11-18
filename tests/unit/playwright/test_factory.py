from pathlib import Path
from unittest.mock import patch

from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.docker.factory import Factory as DockerFactory
from kloudkit.testshed.playwright.factory import Factory

import pytest


MODULE = "kloudkit.testshed.playwright.factory"


def _state(**kwargs) -> ShedState:
  return ShedState.create(
    project_name="project",
    image="test",
    tag="tests",
    src_path=Path("/test/src"),
    tests_path=Path("/test/tests"),
    stubs_path=Path("/test/stubs"),
    container_logs=None,
    **kwargs,
  )


@pytest.mark.parametrize(
  ("kwargs", "image"),
  [
    ({}, "mcr.microsoft.com/playwright:v1.65.1-noble"),
    (
      {"playwright_image": "mirror.example/playwright"},
      "mirror.example/playwright:v1.65.1-noble",
    ),
  ],
)
def test_image_and_server_follow_the_installed_playwright(kwargs, image):
  with (
    patch(
      "kloudkit.testshed.playwright.factory.version", return_value="1.65.1"
    ),
    patch.object(DockerFactory, "build") as build,
  ):
    Factory(_state(**kwargs))(port=4000)

  assert build.call_args.args[0] == image
  assert (
    "npx -y playwright@1.65.1 run-server"
    in build.call_args.kwargs["command"][2]
  )
