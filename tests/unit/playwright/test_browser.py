from unittest.mock import Mock

from kloudkit.testshed.playwright.browser import Browser

import pytest


CLIPBOARD = ["clipboard-read", "clipboard-write"]


@pytest.mark.parametrize("method", ["new_context", "new_page"])
def test_grants_clipboard_permissions(method):
  native = Mock()

  result = getattr(Browser(native), method)()

  getattr(native, method).assert_called_once_with(permissions=CLIPBOARD)
  assert result is getattr(native, method).return_value


@pytest.mark.parametrize("method", ["new_context", "new_page"])
def test_keeps_requested_permissions_and_options(method):
  native = Mock()

  getattr(Browser(native), method)(
    permissions=["geolocation", "clipboard-read"], locale="he-IL"
  )

  getattr(native, method).assert_called_once_with(
    permissions=[*CLIPBOARD, "geolocation"], locale="he-IL"
  )


def test_delegates_everything_else():
  native = Mock()

  Browser(native).close()

  native.close.assert_called_once_with()
