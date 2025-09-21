from kloudkit.testshed.docker.decorators import (
  shed_config,
  shed_env,
  shed_volumes,
)
from kloudkit.testshed.docker.volumes.inline_volume import InlineVolume
from kloudkit.testshed.docker.volumes.remote_volume import RemoteVolume


@shed_env(HELLO="world")
def test_env_decorator(shed):
  assert shed.execute(["echo", "$HELLO"]) == "world"


@shed_volumes(("sample.txt", "/test/sample.txt"))
def test_volume_pointing_to_stubs(shed):
  assert shed.execute(["cat", "/test/sample.txt"]) == "Hello from stub file"


@shed_volumes(("/etc/hostname", "/test/hostname"))
def test_volume_pointing_to_absolute_path(shed):
  assert shed.execute(["cat", "/test/hostname"])


@shed_volumes(InlineVolume("/test/inline.txt", "test content"))
def test_volume_with_inline_volume(shed):
  assert shed.execute(["cat", "/test/inline.txt"]) == "test content"


@shed_volumes(
  RemoteVolume(
    "/test/readme.md",
    "https://raw.githubusercontent.com/kloudkit/testshed/main/README.md",
  )
)
def test_volume_with_remote_volume(shed):
  assert "# KloudKIT TestShed" in shed.execute(["cat", "/test/readme.md"])


@shed_config(workdir="/tmp")
def test_config(shed):
  assert shed.execute(["pwd"]) == "/tmp"
