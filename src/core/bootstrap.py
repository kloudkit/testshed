from pathlib import Path

from python_on_whales import docker

import pytest


def init_shed_network(network: str) -> None:
  """Ensure the required Docker network exists."""

  if not docker.network.exists(network):
    docker.network.create(network)


def init_shed_image(
  image: str,
  *,
  require_local_image: bool,
  force_build: bool,
  context_path: Path,
) -> None:
  """Build the Docker image when missing or rebuild is forced."""

  image_missing = not docker.image.exists(image)

  if image_missing and require_local_image:
    pytest.exit(f"Required image [{image}] not found. Aborting")

  if image_missing:
    print(f"Testing image [{image}] not found")
    force_build = True

  if force_build:
    print(f"Forcing build of test image [{image}]")

    docker.build(
      context_path=context_path,
      pull=True,
      progress="plain",
      tags=image,
    )
