from python_on_whales import docker


def init_testing_network(network: str):
  """Ensure the required Docker network exists."""

  if not docker.network.exists(network):
    print(f"Docker network [{network}] not found, creating it")
    docker.network.create(network)
