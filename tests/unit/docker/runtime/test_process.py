from unittest.mock import Mock

from kloudkit.testshed.docker.runtime.process import Process
from kloudkit.testshed.docker.runtime.shell import Result


def _process(stdout):
  wrapped = Mock()
  wrapped.execute.return_value = Result(1, stdout, "")

  return wrapped, Process(wrapped)


def test_pids_matches_the_full_command_line_across_arguments():
  wrapped, process = _process(
    "==> /proc/100/cmdline <==\nws-cli\0serve\0metrics\0\n"
    "==> /proc/7/cmdline <==\nsleep\0infinity\0\n"
    "==> /proc/55/cmdline <==\nws-cli\0serve\0metrics\0"
  )

  assert process.pids("ws-cli serve metrics", full=True) == (55, 100)
  wrapped.execute.assert_called_once_with(
    "tail -n +1 /proc/[0-9]*/cmdline", check=False
  )


def test_pids_matches_the_exact_process_name():
  wrapped, process = _process(
    "==> /proc/100/comm <==\nsleep\n\n"
    "==> /proc/7/comm <==\nsleeper\n\n"
    "==> /proc/55/comm <==\nsleep\n"
  )

  assert process.pids("sleep") == (55, 100)
  wrapped.execute.assert_called_once_with(
    "tail -n +1 /proc/[0-9]*/comm", check=False
  )
