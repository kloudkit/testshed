from unittest.mock import Mock, patch

from kloudkit.testshed.plugin.session import (
  pytest_keyboard_interrupt,
  pytest_sessionfinish,
)


def test_keyboard_interrupt_does_not_raise():
  excinfo = Mock()
  pytest_keyboard_interrupt(excinfo)


@patch("kloudkit.testshed.plugin.session.Cleanup")
def test_sessionfinish_runs_cleanup(mock_cleanup_cls):
  session = Mock()
  session.config.shed = Mock()

  pytest_sessionfinish(session)

  mock_cleanup_cls.assert_called_once_with(session.config.shed)
  mock_cleanup_cls.return_value.run.assert_called_once_with(network=True)


@patch("kloudkit.testshed.plugin.session.Cleanup")
def test_sessionfinish_skips_cleanup_when_no_shed(mock_cleanup_cls):
  session = Mock(spec=["config"])
  session.config = Mock(spec=[])

  pytest_sessionfinish(session)

  mock_cleanup_cls.assert_not_called()
