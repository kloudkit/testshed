from pathlib import Path


def test_returns_tests_path(test_root):
  path = Path(__file__).parents[3] / "tests"

  assert path == test_root
  assert isinstance(test_root, Path)


def test_returns_project_path(project_root):
  path = Path(__file__).parents[3] / "src"

  assert path == project_root
  assert isinstance(project_root, Path)
