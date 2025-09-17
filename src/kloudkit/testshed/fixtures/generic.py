from pathlib import Path

from kloudkit.testshed._internal.state import get_state
from kloudkit.testshed.utils.http import download

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

    content = download(
      url,
      method=method,
      allow_redirects=allow_redirects,
      raise_for_status=raise_for_status,
      request_options=request_options,
    )

    output_path.write_bytes(content)

    return output_path

  return _wrapper
