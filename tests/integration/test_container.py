from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probes.http_probe import HttpProbe
from kloudkit.testshed.docker.probes.readiness_check import ReadinessCheck

import pytest


def test_run_string(docker_sidecar):
  result = docker_sidecar("alpine", command=["echo", "test"], detach=False)

  assert result == "test"


def test_run_container(docker_sidecar):
  result = docker_sidecar("alpine", detach=True)

  assert isinstance(result, Container)


def test_ip_via_hostname(docker_sidecar):
  container = docker_sidecar(
    "alpine", command=["sleep", "infinity"], detach=True
  )

  ip = container.ip()

  assert ip
  assert all(part.isdigit() for part in ip.split("."))


def test_ip_fallback(docker_sidecar):
  container = docker_sidecar(
    "minio/minio", command=["server", "/data"], detach=True
  )

  ip = container.ip()

  assert ip
  assert all(part.isdigit() for part in ip.split("."))


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
