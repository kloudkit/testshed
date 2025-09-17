from dataclasses import dataclass
from pathlib import Path

from kloudkit.testshed.docker.volumes.base_volume import BaseVolume
from kloudkit.testshed.utils.http import download


@dataclass
class RemoteVolume(BaseVolume):
  def __init__(
    self,
    path: Path | str,
    url: str,
    *,
    mode=0o644,
    method="get",
    allow_redirects=True,
    raise_for_status=True,
    request_options=None,
  ):
    super().__init__(path, _mode=mode)
    self._url = url
    self._method = method
    self._allow_redirects = allow_redirects
    self._raise_for_status = raise_for_status
    self._request_options = request_options

  def _get_content(self) -> bytes:
    """Download content from the remote URL."""

    return download(
      self._url,
      method=self._method,
      allow_redirects=self._allow_redirects,
      raise_for_status=self._raise_for_status,
      request_options=self._request_options,
    )
