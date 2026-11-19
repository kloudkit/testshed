import shlex

from kloudkit.testshed.docker.decorators import shed_mutable, shed_volumes

import pytest


VOLUMES = [
  ("a.json", "/tmp/a.json"),
  ("a.yaml", "/tmp/a.yaml"),
  ("a.toml", "/tmp/a.toml"),
  ("sample.txt", "/tmp/sample.txt"),
  (".hidden", "/tmp/.hidden"),
]


@shed_volumes(*VOLUMES)
def test_exists(shed):
  assert shed.fs.exists("/tmp/a.json")
  assert not shed.fs.exists("/tmp/not-a-file")


@shed_volumes(*VOLUMES)
def test_json(shed):
  assert shed.fs.json("/tmp/a.json") == {"hello": "world"}


@shed_volumes(*VOLUMES)
def test_yaml(shed):
  assert shed.fs.yaml("/tmp/a.yaml") == {"hello": "world"}


@shed_volumes(*VOLUMES)
def test_toml(shed):
  assert shed.fs.toml("/tmp/a.toml") == {
    "hello": "world",
    "nested": {"answer": 42},
  }


@shed_mutable()
def test_writable(shed):
  shed.execute("touch /tmp/root-only && chmod 600 /tmp/root-only")

  assert shed.fs.writable("/tmp")
  assert shed.fs.writable("/tmp/root-only")
  assert not shed.fs.writable("/tmp/root-only", user="nobody")


@shed_volumes(*VOLUMES)
def test_text(shed):
  assert shed.fs.text("/tmp/sample.txt") == "Hello from stub file\n"

  assert shed.fs("/tmp/sample.txt") == shed.fs.text("/tmp/sample.txt")


@shed_volumes(*VOLUMES)
def test_bytes(shed):
  assert shed.fs.bytes("/tmp/sample.txt") == b"Hello from stub file\n"


@shed_volumes(*VOLUMES)
def test_ls(shed):
  listing = shed.fs.ls("/tmp")

  assert "a.json" in listing
  assert "a.yaml" in listing
  assert "sample.txt" in listing
  assert ".hidden" not in listing


@shed_volumes(*VOLUMES)
def test_ls_hidden(shed):
  listing = shed.fs.ls("/tmp", hidden=True)

  assert ".hidden" in listing


@shed_volumes(*VOLUMES)
@pytest.mark.parametrize(
  ("path", "mode"),
  [("/tmp/sample.txt", "644"), ("/tmp", "1777")],
)
def test_mode(shed, path, mode):
  actual_mode = shed.fs.mode(path)

  assert isinstance(actual_mode, str)
  assert actual_mode.isdigit()
  assert actual_mode == mode


def test_ownership(shed):
  assert shed.fs.owner("/etc/hostname") == "root"
  assert shed.fs.group("/etc/hostname") == "root"


def test_missing_file_fails_cleanly(shed):
  with pytest.raises(pytest.fail.Exception):
    shed.fs.bytes("/tmp/not-a-file")


@shed_mutable()
def test_paths_with_shell_characters(shed):
  for path in ("/tmp/a b", "/tmp/x$y", "/tmp/it's"):
    shed.execute(["mkdir", "-m", "750", shlex.quote(path)])

    assert shed.fs.exists(path)
    assert shed.fs.writable(path)
    assert shed.fs.mode(path) == "750"
    assert shed.fs.ls(path) == ()
