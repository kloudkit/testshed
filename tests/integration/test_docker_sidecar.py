from kloudkit.testshed.docker import Container, HttpProbe, LogProbe, ShellProbe


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


def test_nginx_with_log_probe(docker_sidecar):
  container = docker_sidecar(
    image="nginx:1.27-alpine",
    probe=LogProbe(pattern=r"start worker process", timeout=5.0),
  )

  assert isinstance(container, Container)
  assert container.state.running


def test_alpine_with_shell_probe(docker_sidecar):
  container = docker_sidecar(
    image="alpine:latest",
    command=["sh", "-c", "sleep 1 && touch /tmp/ready && sleep 30"],
    probe=ShellProbe(command="test -f /tmp/ready", timeout=5.0),
  )

  assert isinstance(container, Container)
  assert container.execute(["cat", "/tmp/ready"]) == ""
