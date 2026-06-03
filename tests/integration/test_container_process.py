import pytest


def test_pids_matches_running_process(shed):
  pids = shed.proc.pids("sleep")

  assert pids
  assert all(isinstance(pid, int) for pid in pids)


def test_pids_empty_for_unknown_process(shed):
  assert shed.proc.pids("no-such-process") == ()


def test_running(shed):
  assert shed.proc.running("sleep")
  assert not shed.proc.running("no-such-process")


def test_cmdline(shed):
  assert "infinity" in shed.proc.cmdline("sleep")


def test_cmdline_raises_for_unknown_process(shed):
  with pytest.raises(LookupError):
    shed.proc.cmdline("no-such-process")


def test_environ(shed):
  assert "PATH" in shed.proc.environ()
