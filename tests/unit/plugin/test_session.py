from unittest.mock import Mock

from kloudkit.testshed.plugin.session import pytest_keyboard_interrupt


def test_keyboard_interrupt_does_not_raise():
  excinfo = Mock()
  pytest_keyboard_interrupt(excinfo)
