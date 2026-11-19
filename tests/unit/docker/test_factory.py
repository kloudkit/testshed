from unittest.mock import MagicMock

from kloudkit.testshed.docker import ShellProbe
from kloudkit.testshed.docker.factory import Factory


def _probe_passed(shed_state, **kwargs):
  container_class = MagicMock()

  Factory(shed_state).build("img", container_class=container_class, **kwargs)

  return container_class.run.call_args.kwargs["probe"]


def test_timeout_is_applied_to_the_probe(shed_state):
  probe = _probe_passed(
    shed_state, probe=ShellProbe(command="true"), timeout=99
  )

  assert probe.timeout == 99


def test_timeout_without_probe_starts_no_probe(shed_state):
  assert _probe_passed(shed_state, timeout=99) is None
