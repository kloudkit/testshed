from importlib.metadata import version

from kloudkit.testshed.docker import (
  Container,
  Factory as DockerFactory,
  HttpProbe,
)
from kloudkit.testshed.utils.network import available_port


class Factory(DockerFactory):
  def __call__(self, *, port: int | None = None) -> Container | str:
    """Create a playwright factory."""

    playwright_version = version("playwright")

    port = port or available_port()
    internal_port = 3000

    return super().build(
      f"mcr.microsoft.com/playwright:v{playwright_version}-noble",
      init=True,
      publish=[(port, internal_port)],
      command=[
        "/bin/sh",
        "-c",
        (
          f"npx -y playwright@{playwright_version}"
          f" run-server --port {internal_port} --host 0.0.0.0"
        ),
      ],
      probe=HttpProbe(port=internal_port),
    )
