import pytest


pytest_plugins = ["kloudkit.testshed.fixtures"]


@pytest.fixture(scope="session")
def shed_container_defaults():
  return {
    "command": ["sleep", "infinity"],
    "detach": True,
  }
