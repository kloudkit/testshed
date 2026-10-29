from playwright.sync_api import (
  Browser as NativeBrowser,
  BrowserContext,
  Page,
)

from kloudkit.testshed.core.wrapper import Wrapper


class Browser(Wrapper[NativeBrowser]):
  PERMISSIONS = ("clipboard-read", "clipboard-write")

  def _with_permissions(self, kwargs: dict) -> dict:
    """Add the default permissions to a context's options."""

    requested = kwargs.get("permissions") or []

    return {
      **kwargs,
      "permissions": list(dict.fromkeys([*self.PERMISSIONS, *requested])),
    }

  def new_context(self, **kwargs) -> BrowserContext:
    """Create a context with the default permissions granted."""

    return self._wrapped.new_context(**self._with_permissions(kwargs))

  def new_page(self, **kwargs) -> Page:
    """Create a page in its own context, with the default permissions."""

    return self._wrapped.new_page(**self._with_permissions(kwargs))
