from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probes.http_probe import HttpProbe
from kloudkit.testshed.docker.probes.readiness_check import ReadinessCheck
from kloudkit.testshed.docker.probes.shell_probe import ShellProbe

import pytest


def test_run_string(docker_sidecar):
  result = docker_sidecar("alpine", command=["echo", "test"], detach=False)

  assert result == "test"


def test_run_container(docker_sidecar):
  result = docker_sidecar("alpine", detach=True)

  assert isinstance(result, Container)


def test_ip(docker_sidecar):
  container = docker_sidecar(
    "alpine", command=["sleep", "infinity"], detach=True
  )

  ip = container.ip()

  assert ip
  assert all(part.isdigit() for part in ip.split("."))


def test_ip_fallback(docker_sidecar):
  container = docker_sidecar("registry.k8s.io/pause:3.10", detach=True)

  ip = container.ip()

  assert ip
  assert all(part.isdigit() for part in ip.split("."))


def test_whoami(docker_sidecar):
  container = docker_sidecar(
    "alpine", command=["sleep", "infinity"], detach=True
  )

  assert container.whoami() == "root"


def test_readiness_timeout(docker_sidecar):
  container = docker_sidecar(
    "alpine", command=["sleep", "infinity"], detach=True
  )

  readiness_check = ReadinessCheck(
    container, HttpProbe(host="http://unreachable", timeout=0.1)
  )

  with pytest.raises(pytest.fail.Exception) as exc_info:
    readiness_check.wait()

  assert "http://unreachable" in str(exc_info.value)
  assert "0.1s" in str(exc_info.value)


def test_env_returns_the_shell_environment(shed):
  environ = shed.env(envs={"MULTI": "a\nb", "EMPTY": ""})

  assert environ["PATH"]
  assert environ["MULTI"] == "a\nb"
  assert environ["EMPTY"] == ""


def test_env_returns_one_value(shed):
  assert shed.env("HOME") == "/root"
  assert shed.env("HOME", user="nobody") == "/nonexistent"
  assert shed.env("NOT_SET") is None


def test_wait_polls_a_probe_mid_test(shed):
  shed.execute("(sleep 1; touch /tmp/ready) > /dev/null 2>&1 &")

  shed.wait(probe=ShellProbe(command="test -e /tmp/ready"), timeout=10.0)
