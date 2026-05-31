from kloudkit.testshed.docker.probes.http_probe import HttpProbe
from kloudkit.testshed.docker.probes.log_probe import LogProbe
from kloudkit.testshed.docker.probes.probe import Probe
from kloudkit.testshed.docker.probes.shell_probe import ShellProbe


def test_default_no_override():
  result = Probe.resolve(default=HttpProbe(port=8080), user=...)
  assert result == HttpProbe(port=8080)


def test_http_merge_user_http():
  result = Probe.resolve(
    default=HttpProbe(port=8080),
    user=HttpProbe(endpoint="/ready"),
  )
  assert result == HttpProbe(port=8080, endpoint="/ready")


def test_shell_replaces_http():
  result = Probe.resolve(
    default=HttpProbe(port=8080),
    user=ShellProbe(command="pg_isready"),
  )
  assert result == ShellProbe(command="pg_isready")


def test_none_disables_probe():
  result = Probe.resolve(default=HttpProbe(port=8080), user=None)
  assert result is None


def test_no_default_with_user_shell():
  result = Probe.resolve(default=None, user=ShellProbe(command="pg_isready"))
  assert result == ShellProbe(command="pg_isready")


def test_http_replaces_shell():
  result = Probe.resolve(
    default=ShellProbe(command="check"),
    user=HttpProbe(port=3000),
  )
  assert result == HttpProbe(port=3000)


def test_no_default_no_user():
  result = Probe.resolve(default=None, user=...)
  assert result is None


def test_timeout_overlays_default_log_probe():
  default = LogProbe(pattern="listening")
  result = Probe.resolve(default=default, user=..., timeout=90.0)

  assert result == LogProbe(pattern="listening", timeout=90.0)


def test_timeout_overlays_without_changing_probe_type():
  default = LogProbe(pattern="listening")
  result = Probe.resolve(default=default, user=..., timeout=90.0)

  assert isinstance(result, LogProbe)
  assert result.timeout == 90.0


def test_timeout_overlays_merged_user_probe():
  result = Probe.resolve(
    default=HttpProbe(port=8080, endpoint="/healthz"),
    user=HttpProbe(timeout=15.0),
    timeout=99.0,
  )

  assert result == HttpProbe(port=8080, endpoint="/healthz", timeout=99.0)


def test_timeout_overlays_cross_type_user_probe():
  result = Probe.resolve(
    default=LogProbe(pattern="listening"),
    user=HttpProbe(port=80),
    timeout=120.0,
  )

  assert result == HttpProbe(port=80, timeout=120.0)


def test_timeout_ignored_when_probe_is_none():
  result = Probe.resolve(default=None, user=..., timeout=120.0)
  assert result is None


def test_no_timeout_leaves_default_untouched():
  default = LogProbe(pattern="listening")
  result = Probe.resolve(default=default, user=...)

  assert result == default
  assert result.timeout == 30.0
