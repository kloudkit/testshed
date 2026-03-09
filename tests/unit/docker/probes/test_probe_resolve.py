from kloudkit.testshed.docker.probes.http_probe import HttpProbe
from kloudkit.testshed.docker.probes.probe import Probe
from kloudkit.testshed.docker.probes.shell_probe import ShellProbe


def test_default_http_no_override():
  result = Probe.resolve(default=HttpProbe(port=8080), user=..., port=None)
  assert result == HttpProbe(port=8080)


def test_default_http_with_port():
  result = Probe.resolve(default=HttpProbe(port=8080), user=..., port=9090)
  assert result == HttpProbe(port=9090)


def test_http_merge_user_http():
  result = Probe.resolve(
    default=HttpProbe(port=8080),
    user=HttpProbe(endpoint="/ready"),
    port=None,
  )
  assert result == HttpProbe(port=8080, endpoint="/ready")


def test_shell_replaces_http():
  result = Probe.resolve(
    default=HttpProbe(port=8080),
    user=ShellProbe(command="pg_isready"),
    port=None,
  )
  assert result == ShellProbe(command="pg_isready")


def test_none_disables_probe():
  result = Probe.resolve(
    default=HttpProbe(port=8080),
    user=None,
    port=None,
  )
  assert result is None


def test_no_default_with_user_shell():
  result = Probe.resolve(
    default=None,
    user=ShellProbe(command="pg_isready"),
    port=None,
  )
  assert result == ShellProbe(command="pg_isready")


def test_http_replaces_shell():
  result = Probe.resolve(
    default=ShellProbe(command="check"),
    user=HttpProbe(port=3000),
    port=None,
  )
  assert result == HttpProbe(port=3000)


def test_port_ignored_for_shell_default():
  shell = ShellProbe(command="check")
  result = Probe.resolve(default=shell, user=..., port=9090)
  assert result == shell


def test_no_default_no_user():
  result = Probe.resolve(default=None, user=..., port=None)
  assert result is None
