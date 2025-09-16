from pathlib import Path

import requests

from kloudkit.testshed._internal.state import get_state

import pytest


@pytest.fixture(scope="session")
def test_root() -> Path:
  """Absolute path to the tests root."""

  return get_state().tests_path


@pytest.fixture(scope="session")
def project_root() -> Path:
  """Absolute path to the project source root."""

  return get_state().src_path


@pytest.fixture
def downloader(tmp_path):
  """Download a URL to a file in a temporary directory."""

  tmp_path.chmod(0o755)

  def _wrapper(
    url: str,
    output: str,
    *,
    method: str = "get",
    allow_redirects: bool = True,
    raise_for_status: bool = True,
    request_options: dict | None = None,
  ) -> Path:
    output_path = tmp_path / output
    request_options = request_options or {}

    response = requests.request(
      method,
      url,
      allow_redirects=allow_redirects,
      **request_options,
    )

    if raise_for_status:
      response.raise_for_status()

    output_path.write_bytes(response.content)

    return output_path

  return _wrapper
