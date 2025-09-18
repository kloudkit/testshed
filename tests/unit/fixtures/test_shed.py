from kloudkit.testshed.core.state import ShedState


def test_returns_image_and_tag(shed_tag):
  assert shed_tag == "debian:13"
  assert isinstance(shed_tag, str)


def test_returns_shed_state(shed_state):
  assert isinstance(shed_state, ShedState)
