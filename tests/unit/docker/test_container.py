from types import SimpleNamespace
from unittest.mock import patch

from kloudkit.testshed.docker.container import Container


def test_attach_wraps_existing_container():
  native = SimpleNamespace(id="abcdef012345", name="demo")

  with patch(
    "kloudkit.testshed.docker.container.docker.container.inspect",
    return_value=native,
  ) as inspect:
    container = Container.attach("demo", container_logs=True)

  inspect.assert_called_once_with("demo")
  assert container.wrapped is native
  assert container._get("container_logs") is True


def test_container_repr_uses_name_and_short_id():
  native = SimpleNamespace(id="304f3eaa024d1234", name="relaxed_satoshi")
  container = Container(native)

  assert repr(container) == "Container(name='relaxed_satoshi', id='304f3eaa')"


def test_container_repr_drops_noisy_kwargs():
  native = SimpleNamespace(id="abcdef012345", name="demo")
  container = Container(native, container_logs=lambda *_: None)

  result = repr(container)

  assert "container_logs" not in result
  assert result == "Container(name='demo', id='abcdef01')"


def test_container_repr_subclass_name():
  class _WSContainer(Container):
    pass

  native = SimpleNamespace(id="abcdef012345", name="demo")

  assert (
    repr(_WSContainer(native)) == "_WSContainer(name='demo', id='abcdef01')"
  )


def test_container_repr_falls_back_to_wrapped_repr():
  native = SimpleNamespace(id=None, name=None)
  container = Container(native)

  assert repr(container) == f"Container({native!r})"
