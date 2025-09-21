import pytest


def register(config: pytest.Config) -> None:
  """Auto-register TestShed fixtures when shed is enabled."""

  import kloudkit.testshed.fixtures.docker
  import kloudkit.testshed.fixtures.generic
  import kloudkit.testshed.fixtures.playwright
  import kloudkit.testshed.fixtures.shed

  config.pluginmanager.register(kloudkit.testshed.fixtures.docker)
  config.pluginmanager.register(kloudkit.testshed.fixtures.shed)
  config.pluginmanager.register(kloudkit.testshed.fixtures.playwright)
  config.pluginmanager.register(kloudkit.testshed.fixtures.generic)
