from types import SimpleNamespace
from typing import Any, Generic, TypeVar


T = TypeVar("T")


class Wrapper(Generic[T]):
  __slots__ = ("_wrapped", "_args")

  def __init__(self, wrapped: T, **kwargs: Any) -> None:
    self._wrapped: T = wrapped
    self._args = SimpleNamespace(**kwargs)

  def __getattr__(self, name: str) -> Any:
    """Delegate lookups to the wrapped object."""

    return getattr(self._wrapped, name)

  def __dir__(self) -> list[str]:
    """Augment `dir` with attributes from the wrapped object."""

    return sorted(set(super().__dir__()) | set(dir(self._wrapped)))

  def __repr__(self) -> str:
    """Representation of the wrapper, including passed keyword args."""

    args_dict = vars(self._args)
    suffix = ""

    if args_dict:
      kv = ", ".join(f"{k}={args_dict[k]!r}" for k in sorted(args_dict))

      suffix = f", {kv}"

    return f"{type(self).__name__}({self._wrapped!r}{suffix})"

  @property
  def wrapped(self) -> T:
    """Get the underlying wrapped object with its precise type."""

    return self._wrapped
