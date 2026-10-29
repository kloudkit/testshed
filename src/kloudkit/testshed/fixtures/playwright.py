from typing import Generator

from playwright.sync_api import sync_playwright

from kloudkit.testshed.core.state import ShedState
from kloudkit.testshed.playwright.browser import Browser
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
    yield Browser(p.chromium.connect(f"ws://127.0.0.1:{port}"))

  factory.cleanup()
