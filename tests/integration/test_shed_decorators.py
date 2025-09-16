from kloudkit.testshed.docker.decorators import shed_env


@shed_env(HELLO="world")
def test_container_creation(shed):
  assert shed.execute(["echo", "$HELLO"]) == "world"
