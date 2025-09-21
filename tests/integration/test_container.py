from kloudkit.testshed.docker.container import Container
from kloudkit.testshed.docker.probes.http_probe import HttpProbe
from kloudkit.testshed.docker.probes.readiness_check import ReadinessCheck

import pytest


def test_run_string():
  assert Container.run("alpine", ["echo", "test"]) == "test"


def test_run_container():
  result = Container.run("alpine", detach=True)

  assert isinstance(result, Container)


def test_readiness_timeout():
  container = Container.run("alpine", detach=True)

  readiness_check = ReadinessCheck(
    container, HttpProbe(host="http://unreachable", timeout=0.1)
  )

  with pytest.raises(pytest.fail.Exception) as exc_info:
    readiness_check.wait()

  assert "http://unreachable" in str(exc_info.value)
  assert "0.1s" in str(exc_info.value)
