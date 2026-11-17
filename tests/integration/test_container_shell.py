from kloudkit.testshed.docker import Result

import pytest


def test_uses_sh_shell(shed):
  result = shed.execute.sh(["echo", "$0"])

  assert result == "sh" or result.endswith("/sh")


def test_uses_bash_shell(shed):
  result = shed.execute.bash(["echo", "$0"])

  assert result == "bash" or result.endswith("/bash")


def test_execute_default_shell(shed):
  result = shed.execute(["echo", "$0"])

  assert result == "sh" or result.endswith("/sh")


@pytest.mark.parametrize("method", ["sh", "bash", None])
def test_check_false_returns_the_exit_code_and_both_streams(shed, method):
  run = getattr(shed.execute, method) if method else shed.execute

  result = run("echo out; echo err >&2; exit 3", check=False)

  assert result == Result(3, "out", "err")
  assert not result.ok


def test_check_false_keeps_stderr_on_success(shed):
  result = shed.execute("echo warn >&2", check=False)

  assert result.ok
  assert result.stderr == "warn"


def test_check_false_passes_exec_options(shed):
  result = shed.execute(
    "echo $(whoami) $(pwd) $GREETING",
    check=False,
    user="nobody",
    workdir="/tmp",
    envs={"GREETING": "hi"},
  )

  assert result.stdout == "nobody /tmp hi"
