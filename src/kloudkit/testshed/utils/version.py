import re

from packaging.version import Version

import pytest


_SEMVER_RE = re.compile(
  r"""
    (?P<major>\d+)
    \.
    (?P<minor>\d+)
    (?:\.(?P<patch>\d+))?
    (?:[-+~][0-9A-Za-z.~\-]*)?
    """,
  re.VERBOSE,
)


def semver(version: str, fallback: int | str = 0) -> Version:
  """Extract the semver x.y.z (optionally followed by -/+/~)."""

  match = _SEMVER_RE.search(version)

  if not version:
    pytest.fail("No version provided", pytrace=False)

  if not match:
    pytest.fail(f"No version pattern found in: {version!r}", pytrace=False)

  return Version(
    f"{match['major']}.{match['minor']}.{match['patch'] or fallback}"
  )
