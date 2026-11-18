import shlex

from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.runtime.error_handler import error_handler


class Process(Wrapper["Container"]):
  @error_handler
  def pids(self, name: str, *, full: bool = False) -> tuple[int, ...]:
    """Retrieve PIDs by process name, or by command line with `full=True`."""

    if full:
      output = self._wrapped.execute(
        "tail -n +1 /proc/[0-9]*/cmdline", check=False
      ).stdout
      sections = (
        section.partition("/cmdline <==\n")
        for section in output.split("==> /proc/")[1:]
      )
      matches = (
        pid for pid, _, cmd in sections if name in cmd.replace("\0", " ")
      )
    else:
      output = self._wrapped.execute(
        f"grep -Flx {shlex.quote(name)} /proc/[0-9]*/comm", check=False
      ).stdout
      matches = (line.split("/")[2] for line in output.splitlines())

    return tuple(sorted(int(pid) for pid in matches))

  def running(self, name: str, *, full: bool = False) -> bool:
    """Check whether a process named `name` is running."""

    return bool(self.pids(name, full=full))

  @error_handler
  def cmdline(self, name: str, *, full: bool = False) -> str:
    """Retrieve the space-joined command line of the first `name` match."""

    pids = self.pids(name, full=full)

    if not pids:
      raise LookupError(f"no running process named {name!r}")

    return self._wrapped.execute(f"tr '\\0' ' ' < /proc/{pids[0]}/cmdline")

  @error_handler
  def environ(self, pid: int | str = 1, **kwargs) -> dict[str, str]:
    """Retrieve the environment of `pid` as a dict."""

    raw = self._wrapped.execute(f"cat /proc/{pid}/environ", **kwargs)

    return dict(entry.partition("=")[::2] for entry in raw.split("\0") if entry)
