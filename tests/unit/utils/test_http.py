from unittest.mock import Mock, patch

from kloudkit.testshed.utils.http import download


@patch("kloudkit.testshed.utils.http.requests.request")
def test_download_basic(mock_request):
  mock_response = Mock()
  mock_response.content = b"hello"
  mock_request.return_value = mock_response

  result = download("https://example.com/file")

  mock_request.assert_called_once_with(
    "get",
    "https://example.com/file",
    allow_redirects=True,
  )
  mock_response.raise_for_status.assert_called_once()
  assert result == b"hello"


@patch("kloudkit.testshed.utils.http.requests.request")
def test_download_skips_raise_for_status(mock_request):
  mock_response = Mock()
  mock_response.content = b"error page"
  mock_request.return_value = mock_response

  result = download("https://example.com/file", raise_for_status=False)

  mock_response.raise_for_status.assert_not_called()
  assert result == b"error page"


@patch("kloudkit.testshed.utils.http.requests.request")
def test_download_with_custom_method_and_options(mock_request):
  mock_response = Mock()
  mock_response.content = b"data"
  mock_request.return_value = mock_response

  result = download(
    "https://example.com/api",
    method="post",
    allow_redirects=False,
    request_options={"json": {"key": "value"}},
  )

  mock_request.assert_called_once_with(
    "post",
    "https://example.com/api",
    allow_redirects=False,
    json={"key": "value"},
  )
  assert result == b"data"
