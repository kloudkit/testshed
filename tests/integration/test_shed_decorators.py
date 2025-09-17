from kloudkit.testshed.docker.decorators import shed_env, shed_volumes
from kloudkit.testshed.docker.inline_volume import InlineVolume


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
