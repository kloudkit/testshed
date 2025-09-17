import requests


def download(
    url: str,
    *,
    method: str = "get",
    allow_redirects: bool = True,
    raise_for_status: bool = True,
    request_options: dict | None = None,
) -> bytes:
    """Download content from a URL."""

    request_options = request_options or {}

    response = requests.request(
        method,
        url,
        allow_redirects=allow_redirects,
        **request_options,
    )

    if raise_for_status:
        response.raise_for_status()

    return response.content
