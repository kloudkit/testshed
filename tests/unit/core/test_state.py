import os
from pathlib import Path
from unittest.mock import patch

from kloudkit.testshed.core.state import ShedState


def _create_test_state(project_name: str) -> ShedState:
  return ShedState.create(
    project_name=project_name,
    image="test:latest",
    tag="tests",
    src_path=Path("/test/src"),
    tests_path=Path("/test/tests"),
    stubs_path=Path("/test/stubs"),
  )


@patch.dict(os.environ, {}, clear=True)
def test_generate_name_with_project():
  options = _create_test_state("myproject")

  parts = options.network.split("-")

  assert parts[0] == "testshed"
  assert parts[1] == "myproject"
  assert len(parts[2]) == 4
  assert len(parts) == 3

  assert options.network == options.instance_key
  assert options.labels["com.kloudkit.testshed"] == options.instance_key


@patch.dict(os.environ, {"PYTEST_XDIST_WORKER": "gw0"})
def test_generate_name_with_xdist():
  options = _create_test_state("myproject")

  parts = options.network.split("-")

  assert parts[0] == "testshed"
  assert parts[1] == "myproject"
  assert len(parts[2]) == 4
  assert parts[3] == "gw0"
  assert len(parts) == 4

  assert options.network == options.instance_key
  assert options.labels["com.kloudkit.testshed"] == options.instance_key


def test_generate_name_random_suffix():
  options1 = _create_test_state("test")
  options2 = _create_test_state("test")

  assert options1.network != options2.network

  assert options1.network == options1.instance_key
  assert options1.labels["com.kloudkit.testshed"] == options1.instance_key

  assert options2.network == options2.instance_key
  assert options2.labels["com.kloudkit.testshed"] == options2.instance_key


def test_image_and_tag_with_sha():
  state = ShedState.create(
    project_name="test",
    image="myregistry/myimage",
    tag="sha256:abc123def456",
    src_path=Path("/test/src"),
    tests_path=Path("/test/tests"),
    stubs_path=Path("/test/stubs"),
  )

  assert state.image_and_tag == "myregistry/myimage@sha256:abc123def456"
