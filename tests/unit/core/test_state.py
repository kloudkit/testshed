import os
from pathlib import Path
from unittest.mock import patch

from kloudkit.testshed.core.state import ShedState


def create_test_state(project_name: str) -> ShedState:
  """Helper to create ShedState with test defaults."""
  return ShedState.create(
    project_name=project_name,
    image="test:latest",
    tag="tests",
    src_path=Path("/test/src"),
    tests_path=Path("/test/tests"),
    stubs_path=Path("/test/stubs"),
  )


def test_generate_name_with_project():
  options = create_test_state("myproject")

  parts = options.network.split("-")

  assert parts[0] == "testshed"
  assert parts[1] == "myproject"
  assert len(parts[2]) == 4
  assert len(parts) == 3

  assert options.network == options.instance_key
  assert options.labels["com.kloudkit.testshed"] == options.instance_key


def test_generate_name_with_xdist():
  with patch.dict(os.environ, {"PYTEST_XDIST_WORKER": "gw0"}):
    options = create_test_state("myproject")

    parts = options.network.split("-")

    assert parts[0] == "testshed"
    assert parts[1] == "myproject"
    assert len(parts[2]) == 4
    assert parts[3] == "gw0"
    assert len(parts) == 4

    assert options.network == options.instance_key
    assert options.labels["com.kloudkit.testshed"] == options.instance_key


def test_generate_name_random_suffix():
  options1 = create_test_state("test")
  options2 = create_test_state("test")

  assert options1.network != options2.network

  assert options1.network == options1.instance_key
  assert options1.labels["com.kloudkit.testshed"] == options1.instance_key

  assert options2.network == options2.instance_key
  assert options2.labels["com.kloudkit.testshed"] == options2.instance_key
