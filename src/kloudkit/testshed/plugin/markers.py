import pytest


_MARKERS = (
  "shed_config(**configs): assign generic configs to the `shed` instance",
  "shed_env(**envs): assign environment variables to the `shed` instance",
  (
    "shed_volumes(*mounts): assign volume mounts to the `shed` instance."
    " Supports tuples `(source, dest)` or `BaseVolume` objects"
  ),
  "shed_mutable(): force non-default shed for mutable tests operations",
)


def register(config: pytest.Config) -> None:
  """Register all testshed-specific pytest markers."""

  for marker in _MARKERS:
    config.addinivalue_line("markers", marker)
