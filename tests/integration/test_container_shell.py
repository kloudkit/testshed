def test_uses_sh_shell(shed):
  result = shed.execute.sh(["echo", "$0"])

  assert result == "sh" or result.endswith("/sh")


def test_uses_bash_shell(shed):
  result = shed.execute.bash(["echo", "$0"])

  assert result == "bash" or result.endswith("/bash")


def test_execute_default_shell(shed):
  result = shed.execute(["echo", "$0"])

  assert result == "sh" or result.endswith("/sh")
