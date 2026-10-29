from types import SimpleNamespace
from unittest.mock import MagicMock

from kloudkit.testshed.docker.probes.readiness_check import ReadinessCheck
from kloudkit.testshed.docker.probes.shell_probe import ShellProbe

import pytest


def _container(*, running, exit_code=0, logs="boom\n"):
  container = MagicMock()
  container.state = SimpleNamespace(running=running, exit_code=exit_code)
  container.logs.return_value = logs
  container.execute.side_effect = RuntimeError("not ready")

  return container


def test_returns_once_the_probe_passes():
  container = MagicMock()

  ReadinessCheck(container, ShellProbe(command="true", timeout=1.0)).wait()

  container.reload.assert_not_called()


def test_fails_with_probe_message_on_timeout():
  container = _container(running=True)
  probe = ShellProbe(command="false", timeout=0.3)

  with pytest.raises(pytest.fail.Exception, match="did not succeed within"):
    ReadinessCheck(container, probe).wait()


def test_fails_at_once_with_exit_code_and_logs_when_container_exits():
  container = _container(running=False, exit_code=3)
  probe = ShellProbe(command="false", timeout=30.0)

  with pytest.raises(pytest.fail.Exception) as error:
    ReadinessCheck(container, probe).wait()

  message = str(error.value)

  assert "Container exited with code 3 before it was ready" in message
  assert "Command 'false' did not succeed within 30.0s" in message
  assert "boom" in message
  container.logs.assert_any_call(tail=ReadinessCheck.LOG_TAIL)


def test_omits_log_section_when_logs_are_empty():
  container = _container(running=False, exit_code=1, logs="")

  with pytest.raises(pytest.fail.Exception) as error:
    ReadinessCheck(container, ShellProbe(command="false")).wait()

  assert "last 20 lines" not in str(error.value)


def test_keeps_waiting_when_state_is_unavailable():
  container = _container(running=True)
  container.reload.side_effect = RuntimeError("inspect failed")
  probe = ShellProbe(command="false", timeout=0.3)

  with pytest.raises(pytest.fail.Exception, match="did not succeed within"):
    ReadinessCheck(container, probe).wait()


def test_prints_full_logs_when_asked():
  container = _container(running=False, exit_code=2)
  printer = MagicMock()

  with pytest.raises(pytest.fail.Exception):
    ReadinessCheck(
      container, ShellProbe(command="false"), container_logs=printer
    ).wait()

  printer.assert_called_once_with("boom\n")
