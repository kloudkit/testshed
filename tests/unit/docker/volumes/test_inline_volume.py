import os
from pathlib import Path

from kloudkit.testshed.docker.volumes.inline_volume import InlineVolume


def test_create_temp_file():
  volume = InlineVolume("/path/to/file", "test content")

  temp_path = volume.create()

  assert Path(temp_path).exists()

  with open(temp_path, "rb") as f:
    content = f.read()

  assert content == b"test content"

  stat = os.stat(temp_path)
  assert stat.st_mode & 0o777 == 0o644

  volume.cleanup()


def test_create_temp_file_with_custom_mode():
  volume = InlineVolume("/path/to/file", "test content", mode=0o755)

  temp_path = volume.create()

  stat = os.stat(temp_path)
  assert stat.st_mode & 0o777 == 0o755

  volume.cleanup()


def test_create_returns_same_path_on_multiple_calls():
  volume = InlineVolume("/path/to/file", "test content")

  assert volume.create() == volume.create()

  volume.cleanup()


def test_cleanup_removes_temp_file():
  volume = InlineVolume("/path/to/file", "test content")

  temp_path = volume.create()
  volume.cleanup()

  assert not Path(temp_path).exists()
