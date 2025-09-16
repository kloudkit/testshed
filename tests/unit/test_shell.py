from unittest.mock import Mock

from kloudkit.testshed.docker.runtime.shell import Shell

import pytest


@pytest.fixture
def mock_shell():
  wrapped = Mock()

  return wrapped, Shell(
    wrapped, sh_path="/bin/sh", bash_path="/bin/bash", zsh_path="/usr/bin/zsh"
  )


def test_call_uses_default_shell(mock_shell):
  wrapped, shell = mock_shell

  shell(["echo", "test"])

  wrapped.execute.assert_called_once_with(
    ["/bin/sh", "-c", "echo test"], user=None
  )


def test_call_uses_configured_shell():
  wrapped = Mock()
  shell = Shell(wrapped, sh_path="/bin/sh", shell="/bin/bash")

  shell(["echo", "test"])

  wrapped.execute.assert_called_once_with(
    ["/bin/bash", "-c", "echo test"], user=None
  )


@pytest.mark.parametrize(
  ("method", "path", "expected_shell"),
  [
    ("sh", "sh_path", "/bin/sh"),
    ("bash", "bash_path", "/bin/bash"),
    ("zsh", "zsh_path", "/usr/bin/zsh"),
  ],
)
def test_shell_methods(method, path, expected_shell):
  wrapped = Mock()
  shell = Shell(wrapped, **{path: expected_shell})

  getattr(shell, method)(["echo", "test"])

  wrapped.execute.assert_called_once_with(
    [expected_shell, "-c", "echo test"], user=None
  )


def test_login_shell(mock_shell):
  wrapped, shell = mock_shell

  shell_with_login = Shell(wrapped, sh_path="/bin/sh", login_shell=True)
  shell_with_login.sh(["echo", "test"])

  wrapped.execute.assert_called_with(
    ["/bin/sh", "-cli", "echo test"], user=None
  )


def test_login_shell_as_parameter(mock_shell):
  wrapped, shell = mock_shell

  shell.sh(["echo", "test"], login_shell=True)

  wrapped.execute.assert_called_with(
    ["/bin/sh", "-cli", "echo test"], user=None
  )


def test_user_parameter_override():
  wrapped = Mock()
  shell = Shell(wrapped, sh_path="/bin/sh", user="default_user")

  shell.sh(["echo", "test"], user="override_user")

  wrapped.execute.assert_called_once_with(
    ["/bin/sh", "-c", "echo test"], user="override_user"
  )
