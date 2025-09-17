from python_on_whales.exceptions import DockerException

from kloudkit.testshed.docker.runtime.error_handler import error_message


def _create_docker_error(stdout=b"", stderr=b"", return_code=1):
  return DockerException(
    command_launched=[],
    return_code=return_code,
    stdout=stdout,
    stderr=stderr,
  )


def test_stderr_message():
  error = _create_docker_error(
    stderr=b"cat: can't open '/nonexistent/file': No such file or directory\n"
  )

  expected = "cat: can't open '/nonexistent/file': No such file or directory"

  assert error_message(error) == expected


def test_stdout_message():
  error = _create_docker_error(
    return_code=127,
    stdout=b"OCI runtime exec failed: exec failed: unable to start container "
    b'process: exec: "nonexistent_command": executable file not found '
    b"in $PATH: unknown\n",
  )

  expected = (
    'exec: "nonexistent_command": executable file not found in $PATH: unknown'
  )

  assert error_message(error) == expected


def test_empty_output():
  error = _create_docker_error()

  assert error_message(error) == "Command failed"


def test_prefers_stderr():
  error = _create_docker_error(
    stdout=b"some stdout content", stderr=b"stderr error message"
  )

  assert error_message(error) == "stderr error message"


def test_handles_none_bytes():
  error = _create_docker_error(stdout=None, stderr=None)

  assert error_message(error) == "Command failed"
