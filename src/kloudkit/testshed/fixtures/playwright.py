from typing import Generator

from playwright.sync_api import Browser, sync_playwright

from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.playwright.factory import Factory
from kloudkit.testshed.utils.network import available_port

import pytest


@pytest.fixture(scope="session")
def playwright_browser(shed_state: ShedState) -> Generator[Browser, None, None]:
  """Launch a Playwright browser instance."""

  factory = Factory(shed_state)

  port = available_port()

  factory(port=port)

  with sync_playwright() as p:
    browser = p.chromium.connect(f"ws://127.0.0.1:{port}")

    context = browser.new_context()

    context.grant_permissions(["clipboard-read", "clipboard-write"])

    yield browser

  factory.cleanup()
