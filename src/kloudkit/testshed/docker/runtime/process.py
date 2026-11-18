from kloudkit.testshed.core.wrapper import Wrapper
from kloudkit.testshed.docker.runtime.error_handler import error_handler


class Process(Wrapper["Container"]):
  def _read(self, field: str) -> dict[int, str]:
    """Read `/proc/<pid>/<field>` for every process, by PID."""

    output = self._wrapped.execute(
      f"tail -n +1 /proc/[0-9]*/{field}", check=False
    ).stdout
    entries = (
      entry.partition(f"/{field} <==\n")
      for entry in output.split("==> /proc/")[1:]
    )

    return {
      int(pid): value.replace("\0", " ").strip() for pid, _, value in entries
    }

  @error_handler
  def pids(self, name: str, *, full: bool = False) -> tuple[int, ...]:
    """Retrieve PIDs by process name, or by command line with `full=True`."""

    if full:
      matches = (p for p, cmd in self._read("cmdline").items() if name in cmd)
    else:
      matches = (p for p, comm in self._read("comm").items() if comm == name)

    return tuple(sorted(matches))

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
