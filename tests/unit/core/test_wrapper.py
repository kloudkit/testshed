from types import SimpleNamespace

from kloudkit.testshed.core.wrapper import Wrapper


class MockObject:
  def __init__(self, value: str):
    self.value = value
    self.hidden_attr = "hidden"

  def method(self):
    return f"method called with {self.value}"

  def __str__(self):
    return f"MockObject({self.value})"


def test_wrapper_init():
  obj = MockObject("test")
  wrapper = Wrapper(obj, param1="value1", param2=42)

  assert wrapper.wrapped is obj
  assert isinstance(wrapper._args, SimpleNamespace)
  assert wrapper._args.param1 == "value1"
  assert wrapper._args.param2 == 42


def test_wrapper_getattr_delegation():
  obj = MockObject("test")
  wrapper = Wrapper(obj)

  assert wrapper.value == "test"
  assert wrapper.hidden_attr == "hidden"
  assert wrapper.method() == "method called with test"


def test_wrapper_dir():
  obj = MockObject("test")
  wrapper = Wrapper(obj)

  wrapper_dir = dir(wrapper)
  obj_dir = dir(obj)

  for attr in obj_dir:
    assert attr in wrapper_dir


def test_wrapper_repr_no_args():
  obj = MockObject("test")
  wrapper = Wrapper(obj)

  expected = f"Wrapper({obj!r})"
  assert repr(wrapper) == expected
