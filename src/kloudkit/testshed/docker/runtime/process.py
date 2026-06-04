import shlex

from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.runtime.error_handler import error_handler


class Process(Wrapper["Container"]):
  @error_handler
  def pids(self, name: str) -> tuple[int, ...]:
    """Retrieve PIDs whose process name exactly matches `name`."""

    output = self._wrapped.execute(
      f"grep -Flx {shlex.quote(name)} /proc/[0-9]*/comm 2>/dev/null || true"
    )

    return tuple(int(line.split("/")[2]) for line in output.splitlines())

  def running(self, name: str) -> bool:
    """Check whether a process named `name` is running."""

    return bool(self.pids(name))

  @error_handler
  def cmdline(self, name: str) -> str:
    """Retrieve the space-joined command line of the first `name` match."""

    pids = self.pids(name)

    if not pids:
      raise LookupError(f"no running process named {name!r}")

    return self._wrapped.execute(f"tr '\\0' ' ' < /proc/{pids[0]}/cmdline")

  @error_handler
  def environ(self, pid: int = 1) -> dict[str, str]:
    """Retrieve the environment of `pid` as a dict."""

    raw = self._wrapped.execute(f"tr '\\0' '\\n' < /proc/{pid}/environ")

    return dict(line.partition("=")[::2] for line in raw.splitlines())
