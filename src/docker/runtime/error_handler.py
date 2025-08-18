import functools
from typing import Callable, ParamSpec, TypeVar

from python_on_whales.exceptions import DockerException, NoSuchContainer

import pytest


P = ParamSpec("P")
T = TypeVar("T")


def error_handler(fn: Callable[P, T]) -> Callable[P, T]:
  """Handle Docker related error output."""

  @functools.wraps(fn)
  def _wrapped(self, *args, **kwargs):
    raises = kwargs.pop("raises", False)

    try:
      return fn(self, *args, **kwargs)
    except NoSuchContainer as error:
      failure = str(error)
    except DockerException as error:
      if raises:
        raise

      failure = str(error)

    if failure:
      pytest.fail(failure, pytrace=False)

  return _wrapped
