from pathlib import Path
from typing import Literal

from python_on_whales import docker

import pytest


def _build(image: str, context_path: Path) -> None:
  print(f"Building image [{image}]")
  docker.build(
    context_path=context_path,
    pull=True,
    progress="plain",
    tags=image,
  )


def init_shed_network(network: str) -> None:
  """Ensure the required Docker network exists."""

  if not docker.network.exists(network):
    docker.network.create(network)


def init_shed_image(
  image: str,
  *,
  policy: Literal["pull", "build", "require", "rebuild"],
  context_path: Path,
) -> None:
  """Acquire the Docker image based on the specified policy."""

  image_exists = docker.image.exists(image)

  match policy:
    case "require":
      if not image_exists:
        raise pytest.UsageError(f"Required image [{image}] not found.")

    case "build":
      if not image_exists:
        _build(image, context_path)

    case "rebuild":
      _build(image, context_path)

    case "pull":
      if image_exists:
        return

      try:
        print(f"Testing image [{image}] not found")
        print(f"Attempting to pull image [{image}]")
        docker.pull(image)
      except Exception as e:
        print(f"Pull failed ({e})")
        _build(image, context_path)
