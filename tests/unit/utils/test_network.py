from kloudkit.testshed.utils.network import available_port


def test_gets_available_port():
  port1 = available_port()
  port2 = available_port()

  assert port1 != port2

  assert isinstance(port1, int)
  assert isinstance(port2, int)

  assert 0 < port1 <= 65535
  assert 0 < port2 <= 65535
