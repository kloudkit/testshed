from typing import Generator

from kloudkit.testshed.playwright import Factory
from kloudkit.testshed.utils.network import available_port
from playwright.sync_api import Browser, sync_playwright

import pytest


@pytest.fixture(scope="session")
def playwright_browser() -> Generator[Browser, None, None]:
  """Launch a Playwright browser instance."""

  factory = Factory()

  port = available_port()

  factory(port=port)

  with sync_playwright() as p:
    browser = p.chromium.connect(f"ws://127.0.0.1:{port}")

    context = browser.new_context()

    context.grant_permissions(["clipboard-read", "clipboard-write"])

    yield browser

  factory.cleanup()
