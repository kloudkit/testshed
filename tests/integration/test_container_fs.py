from kloudkit.testshed.docker.decorators import shed_volumes


VOLUMES = [
  ("a.json", "/tmp/a.json"),
  ("a.yaml", "/tmp/a.yaml"),
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
