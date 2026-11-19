def pytest_keyboard_interrupt(excinfo):
  """Handle Ctrl+C interruption during test session."""

  print(
    "\n🛑 Test session interrupted.",
    "Cleanup has started and might take a moment...",
  )
