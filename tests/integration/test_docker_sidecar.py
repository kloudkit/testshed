from kloudkit.testshed.docker import Container, HttpProbe


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


def test_nginx_with_probe(docker_sidecar):
  container = docker_sidecar(
    image="nginx:1.27-alpine",
    probe=HttpProbe(port=80, timeout=3.0),
  )

  assert isinstance(container, Container)
  assert "nginx" in container.execute(["curl", "-s", "http://localhost:80"])
