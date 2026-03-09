from unittest.mock import MagicMock

from kloudkit.testshed.docker.probes.http_probe import HttpProbe
from kloudkit.testshed.docker.probes.probe import Probe

import pytest


def test_default_values():
  probe = HttpProbe()

  assert probe.host == "http://localhost"
  assert probe.port is None
  assert probe.endpoint is None
  assert probe.command == "curl"
  assert probe.timeout == 30.0
  assert probe.url == "http://localhost"


def test_custom_values():
  probe = HttpProbe(
    host="http://example.com",
    port=8080,
    endpoint="/health",
    command="wget",
    timeout=60.0,
  )

  assert probe.host == "http://example.com"
  assert probe.port == 8080
  assert probe.endpoint == "/health"
  assert probe.command == "wget"
  assert probe.timeout == 60.0
  assert probe.url == "http://example.com:8080/health"


def test_merge_with_none_values():
  probe1 = HttpProbe(host="http://localhost", port=8080)
  probe2 = HttpProbe(endpoint="/status")

  merged = probe1.merge(probe2)

  assert merged.host == "http://localhost"
  assert merged.port == 8080
  assert merged.endpoint == "/status"
  assert merged.command == "curl"
  assert merged.timeout == 30.0
  assert merged.url == "http://localhost:8080/status"


def test_merge_overrides_existing():
  probe1 = HttpProbe(host="http://localhost", port=8080, timeout=10.0)
  probe2 = HttpProbe(
    host="http://example.com", endpoint="/health", timeout=60.0
  )

  merged = probe1.merge(probe2)

  assert merged.host == "http://example.com"
  assert merged.port == 8080
  assert merged.endpoint == "/health"
  assert merged.command == "curl"
  assert merged.timeout == 60.0


def test_merge_ignore_none_false():
  probe1 = HttpProbe(host="http://localhost", port=8080)
  probe2 = HttpProbe(endpoint="/status")

  merged = probe1.merge(probe2, ignore_none=False)

  assert merged.host == "http://localhost"
  assert merged.port is None
  assert merged.endpoint == "/status"
  assert merged.command == "curl"
  assert merged.timeout == 30.0


def test_merge_returns_new_instance():
  probe1 = HttpProbe(host="http://localhost")
  probe2 = HttpProbe(port=8080)

  merged = probe1.merge(probe2)

  assert merged is not probe1
  assert merged is not probe2


@pytest.mark.parametrize("ignore_none", [True, False])
def test_merge_empty_probe(ignore_none):
  probe1 = HttpProbe(host="http://localhost", port=8080)
  probe2 = HttpProbe()

  merged = probe1.merge(probe2, ignore_none=ignore_none)

  if ignore_none:
    assert merged.host == "http://localhost"
    assert merged.port == 8080
  else:
    assert merged.host == "http://localhost"
    assert merged.port is None


def test_inherits_from_probe():
  probe = HttpProbe()

  assert isinstance(probe, Probe)


def test_check_executes_command():
  container = MagicMock()
  probe = HttpProbe(port=8080, endpoint="/health")

  probe.check(container)

  container.execute.assert_called_once_with(
    ["curl", "http://localhost:8080/health"], raises=True
  )


def test_check_raises_on_failure():
  container = MagicMock()
  container.execute.side_effect = RuntimeError("connection refused")
  probe = HttpProbe(port=8080)

  with pytest.raises(RuntimeError, match="connection refused"):
    probe.check(container)


def test_failure_message():
  probe = HttpProbe(port=8080, endpoint="/health", timeout=15.0)

  assert probe.failure_message == (
    "URL [http://localhost:8080/health] was not reachable within 15.0s"
  )
