from kloudkit.testshed.docker import (
  Container,
  HttpProbe,
  LogProbe,
  ShellProbe,
  docker,
)

import pytest


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


def test_container_exiting_before_ready_reports_code_and_logs(docker_sidecar):
  with pytest.raises(pytest.fail.Exception) as error:
    docker_sidecar(
      image="alpine:latest",
      command=["sh", "-c", "echo boom; exit 3"],
      probe=ShellProbe(command="test -f /tmp/ready", timeout=30.0),
    )

  message = str(error.value)

  assert "Container exited with code 3 before it was ready" in message
  assert "boom" in message


def test_detached_container_outlives_its_exit(docker_sidecar):
  container = docker_sidecar(
    image="alpine:latest", command=["sh", "-c", "echo done"]
  )

  docker.container.wait(container.wrapped)

  assert container.logs() == "done\n"
