from kloudkit.testshed.docker import Container


def test_container_creation(docker_sidecar):
  container = docker_sidecar(
    image="alpine:latest", command=["sleep", "30"], detach=True
  )

  assert isinstance(container, Container)
  assert container.state.running


def test_container_execute_command(docker_sidecar):
  container = docker_sidecar(
    image="alpine:latest", command=["sleep", "30"], detach=True
  )

  assert container.execute(["echo", "hello world"]) == "hello world"


def test_container_ip_address(docker_sidecar):
  container = docker_sidecar(
    image="alpine:latest", command=["sleep", "30"], detach=True
  )

  assert len(container.ip().split(".")) == 4
