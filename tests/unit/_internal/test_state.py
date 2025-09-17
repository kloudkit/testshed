import os
from unittest.mock import patch

from kloudkit.testshed._internal.state import Options


def test_generate_name_with_project():
  options = Options.create(project_name="myproject")

  parts = options.network.split("-")

  assert parts[0] == "testshed"
  assert parts[1] == "myproject"
  assert len(parts[2]) == 4
  assert len(parts) == 3

  assert options.network == options.instance_key
  assert options.labels["com.kloudkit.testshed"] == options.instance_key


def test_generate_name_with_xdist():
  with patch.dict(os.environ, {"PYTEST_XDIST_WORKER": "gw0"}):
    options = Options.create(project_name="myproject")

    parts = options.network.split("-")

    assert parts[0] == "testshed"
    assert parts[1] == "myproject"
    assert len(parts[2]) == 4
    assert parts[3] == "gw0"
    assert len(parts) == 4

    assert options.network == options.instance_key
    assert options.labels["com.kloudkit.testshed"] == options.instance_key


def test_generate_name_random_suffix():
  options1 = Options.create(project_name="test")
  options2 = Options.create(project_name="test")

  assert options1.network != options2.network

  assert options1.network == options1.instance_key
  assert options1.labels["com.kloudkit.testshed"] == options1.instance_key

  assert options2.network == options2.instance_key
  assert options2.labels["com.kloudkit.testshed"] == options2.instance_key
