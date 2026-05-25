import pytest


@pytest.fixture(scope="session")
def shed_container_defaults():
  return {
    "command": ["sleep", "infinity"],
    "detach": True,
  }
