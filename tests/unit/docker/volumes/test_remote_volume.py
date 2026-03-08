from pathlib import Path
from unittest.mock import patch

from kloudkit.testshed.docker.volumes.remote_volume import RemoteVolume

import pytest


@pytest.fixture
def mock_download():
  with patch("kloudkit.testshed.docker.volumes.remote_volume.download") as mock:
    mock.return_value = b"data"
    yield mock


def test_create_downloads_content(mock_download):
  mock_download.return_value = b"remote content"

  volume = RemoteVolume("/container/path", "https://example.com/file.txt")
  temp_path = volume.create()

  mock_download.assert_called_once_with(
    "https://example.com/file.txt",
    method="get",
    allow_redirects=True,
    raise_for_status=True,
    request_options=None,
  )

  with open(temp_path, "rb") as f:
    assert f.read() == b"remote content"

  volume.cleanup()


def test_create_with_custom_options(mock_download):
  volume = RemoteVolume(
    "/container/path",
    "https://example.com/file.txt",
    method="post",
    allow_redirects=False,
    raise_for_status=False,
    request_options={"headers": {"Authorization": "Bearer token"}},
  )
  volume.create()

  mock_download.assert_called_once_with(
    "https://example.com/file.txt",
    method="post",
    allow_redirects=False,
    raise_for_status=False,
    request_options={"headers": {"Authorization": "Bearer token"}},
  )

  volume.cleanup()


def test_cleanup_removes_temp_file(mock_download):
  volume = RemoteVolume("/container/path", "https://example.com/file.txt")
  temp_path = volume.create()

  assert Path(temp_path).exists()

  volume.cleanup()

  assert not Path(temp_path).exists()
