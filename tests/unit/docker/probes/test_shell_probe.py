from unittest.mock import MagicMock

from kloudkit.testshed.docker.probes.shell_probe import ShellProbe

import pytest


def test_default_values():
  probe = ShellProbe()

  assert probe.command == ""
  assert probe.timeout == 30.0


def test_custom_command_string():
  probe = ShellProbe(command="pg_isready -U postgres", timeout=10.0)

  assert probe.command == "pg_isready -U postgres"
  assert probe.timeout == 10.0


def test_custom_command_list():
  probe = ShellProbe(command=["pg_isready", "-U", "postgres"])

  assert probe.command == ["pg_isready", "-U", "postgres"]


def test_check_splits_string_command():
  container = MagicMock()
  probe = ShellProbe(command="pg_isready -U postgres")

  probe.check(container)

  container.execute.assert_called_once_with(
    ["pg_isready", "-U", "postgres"], raises=True
  )


def test_check_passes_list_command_directly():
  container = MagicMock()
  probe = ShellProbe(command=["pg_isready", "-U", "postgres"])

  probe.check(container)

  container.execute.assert_called_once_with(
    ["pg_isready", "-U", "postgres"], raises=True
  )


def test_check_raises_on_failure():
  container = MagicMock()
  container.execute.side_effect = RuntimeError("command failed")
  probe = ShellProbe(command="false")

  with pytest.raises(RuntimeError, match="command failed"):
    probe.check(container)


def test_failure_message():
  probe = ShellProbe(command="pg_isready -U postgres", timeout=15.0)

  assert probe.failure_message == (
    "Command 'pg_isready -U postgres' did not succeed within 15.0s"
  )
