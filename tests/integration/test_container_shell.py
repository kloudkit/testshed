def test_uses_sh_shell(shed):
  result = shed.execute.sh(["echo", "$0"])

  assert "/bin/sh" in result or "sh" in result


def test_uses_bash_shell(shed):
  result = shed.execute.bash(["echo", "$0"])

  assert "/bin/bash" in result or "bash" in result


def test_execute_default_shell(shed):
  """Test that shed.execute() uses sh shell by default for env var expansion."""
  result = shed.execute(["echo", "$0"])

  assert "/bin/sh" in result or "sh" in result
