import pytest


def print_container_logs(config: pytest.Config, logs: str) -> None:
  """Print container logs with pytest-style section headers."""

  if not logs:
    return

  capman = config.pluginmanager.getplugin("capturemanager")

  if capman:
    capman.suspend_global_capture(in_=False)

  try:
    tw = config.get_terminal_writer()

    tw.line()
    tw.sep("=", "container logs", yellow=True, bold=True)
    tw.write(logs)

    if not logs.endswith("\n"):
      tw.line()

    tw.sep("\u2014", "END container logs", yellow=True, bold=True)
    tw.flush()
  finally:
    if capman:
      capman.resume_global_capture()
