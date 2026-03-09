from unittest.mock import MagicMock

from kloudkit.testshed.docker.probes.log_probe import LogProbe

import pytest


def test_default_values():
  probe = LogProbe()

  assert probe.pattern == ""
  assert probe.timeout == 30.0


def test_custom_values():
  probe = LogProbe(pattern="ready to accept connections", timeout=60.0)

  assert probe.pattern == "ready to accept connections"
  assert probe.timeout == 60.0


def test_check_passes_when_pattern_found():
  container = MagicMock()
  container.logs.return_value = (
    "Server ready to accept connections on port 5432"
  )
  probe = LogProbe(pattern="ready to accept connections")

  probe.check(container)


def test_check_raises_when_pattern_not_found():
  container = MagicMock()
  container.logs.return_value = "Server starting up..."
  probe = LogProbe(pattern="ready to accept connections")

  with pytest.raises(ValueError, match="not found in logs"):
    probe.check(container)


def test_check_supports_regex():
  container = MagicMock()
  container.logs.return_value = "Listening on port 5432"
  probe = LogProbe(pattern=r"Listening on port \d+")

  probe.check(container)


def test_check_regex_no_match():
  container = MagicMock()
  container.logs.return_value = "Starting server"
  probe = LogProbe(pattern=r"Listening on port \d+")

  with pytest.raises(ValueError):  # noqa: PT011
    probe.check(container)


def test_failure_message():
  probe = LogProbe(pattern="ready", timeout=20.0)

  assert probe.failure_message == (
    "Pattern 'ready' not found in container logs within 20.0s"
  )
