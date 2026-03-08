# KloudKIT TestShed

A pytest plugin for integration testing with Docker and Playwright.
It handles container lifecycle, browser provisioning, and cleanup automatically.

## Features

- **Docker management:** provision and control containers from tests.
- **Playwright integration:** browser testing in isolated Docker environments.
- **Configurable via markers & CLI:** tune environments per test or suite.
- **Automatic cleanup:** containers and volumes are removed after tests.

## Installation

```sh
pip install testshed
```

## Usage

### Fixture Auto-Discovery

TestShed fixtures are automatically available when `--shed` is enabled.

```bash
pytest --shed
```

For manual control or when `--shed` is not used, you can still import specific fixtures:

```python
from kloudkit.testshed.fixtures.docker import docker_sidecar
from kloudkit.testshed.fixtures.shed import shed
from kloudkit.testshed.fixtures.playwright import playwright_browser
```

### Docker container testing

TestShed provides fixtures to manage containers inside your tests.

#### Configure containers with decorators

Configure containers using `pytest` markers:

- **`@shed_config(**kwargs)`:** pass arguments to the container factory (e.g. `publish`, `networks`).
- **`@shed_env(**envs)`:** set environment variables.
- **`@shed_volumes(*mounts)`:** mount volumes as `(source, dest)` tuples or `BaseVolume` instances.
- **`@shed_mutable()`:** force a dedicated container for tests that mutate state (bypasses the shared default).

```python
from kloudkit.testshed.docker import InlineVolume, RemoteVolume

@shed_config(publish=[(8080, 80)])
@shed_env(MY_ENV_VAR="hello")
@shed_volumes(
  ("/path/to/host/data", "/app/data"),
  InlineVolume("/app/config.txt", "any content you want", mode=0o644),
  RemoteVolume("/app/remote-config.json", "https://api.example.com/config.json", mode=0o644),
)
def test_configured_docker_app(shed):
  # ... test logic ...
```

Use `@shed_mutable()` when your test writes data, installs packages, or otherwise changes the container.

This ensures it gets its own instance instead of reusing the shared default:

```python
@shed_mutable()
def test_install_package(shed):
  shed.execute("apt-get install -y curl")

  assert "curl" in shed.execute("which curl")
```

#### High-level `shed` fixture

Use the `shed` fixture for container management with configurable defaults:

```python
import pytest

from kloudkit.testshed.docker import Container, HttpProbe

class MyAppContainer(Container):
  DEFAULT_USER = "app"

@pytest.fixture(scope="session")
def shed_container_defaults():
  """Override this fixture to set project-specific defaults."""

  return {
    "container_class": MyAppContainer,
    "envs": {"APP_PORT": 3000},
    "probe": HttpProbe(port=3000, endpoint="/health"),
  }

def test_my_app(shed):
  # Uses your configured defaults automatically
  assert shed.execute("whoami") == "app"

@shed_env(DEBUG="true")
def test_my_app_with_debug(shed):
  # New container with override, merged with defaults
  assert shed.execute("echo $DEBUG") == "true"
  assert shed.execute("echo $APP_PORT") == "3000"
```

#### Deferred deployment with `shed_deferred`

Use `shed_deferred` when you need to control *when* the container starts, for pre-deployment
setup, runtime parameterization, or spinning up multiple containers in a single test:

```python
@shed_env(APP_PORT="3000")
def test_deferred_deployment(shed_deferred):
  # Container is NOT running yet — do setup here
  # ...

  # Deploy with optional call-time overrides
  container = shed_deferred(envs={"DEBUG": "true"})
  # envs are merged: APP_PORT=3000 + DEBUG=true

  assert container.execute("echo $DEBUG") == "true"
  assert container.execute("echo $APP_PORT") == "3000"


def test_multiple_containers(shed_deferred):
  primary = shed_deferred(envs={"ROLE": "primary"})
  replica = shed_deferred(envs={"ROLE": "replica"})
  # Each call spins up a new container
```

Call-time parameters merge with decorator config:

- **`envs`:** dict merge *(call-time values override decorator values)*.
- **`volumes`:** concatenated *(call-time volumes added after decorator volumes)*.
- **`**kwargs`:** passed as config args *(override decorator `@shed_config` values)*.

#### Basic Docker container

For a lower-level API, use the `docker_sidecar` fixture:

```python
def test_my_docker_app(docker_sidecar):
  # Launch a container
  nginx = docker_sidecar("nginx:latest", publish=[(8080, 80)])

  # Execute a command inside the container
  hostname = nginx.execute("cat /etc/hostname")
  assert len(hostname) > 0

  # Access the container's IP
  print(f"Container IP: {nginx.ip()}")

  # Interact with the file system
  assert "html" in nginx.fs.ls("/usr/share/nginx")
```

### Playwright browser testing

Get a Playwright browser instance running in Docker via `playwright_browser`:

```python
def test_example_website(playwright_browser):
  page = playwright_browser.new_page()
  page.goto("http://example.com")
  assert "Example Domain" in page.title()
  # ... more Playwright test logic ...
```

### Command-line options

TestShed extends `pytest` with options to control the Docker environment:

- **`--shed`:** enable TestShed for the current test suite *(default: disabled)*.
- **`--shed-image IMAGE`:** base image *(e.g., `ghcr.io/acme/app`)*.
- **`--shed-tag TAG|SHA`:** image tag or digest *(default: `tests`)*.
- **`--shed-build-context DIR`:** Docker build context *(default: `pytest.ini` directory)*.
- **`--shed-image-policy POLICY`:** image acquisition policy *(default: `pull`)*.
- **`--shed-skip-bootstrap`:** skip Docker bootstrapping *(useful for unit tests)*.
- **`--shed-container-logs`:** print container logs on failure *(default: disabled)*.

> [!NOTE]
> When TestShed is installed globally, you must explicitly enable it per suite with
> `--shed`.
> This prevents it from configuring Docker in projects that don't use it.

#### Image Policies

The `--shed-image-policy` option controls how TestShed acquires Docker images:

- **`pull`** *(default)*: pull image if not found locally, build as fallback.
- **`build`:** build only if image doesn't exist locally.
- **`require`:** require existing local image *(fails if not found)*.
- **`rebuild`:** always rebuild the image.

#### Examples

```bash
# Enable TestShed for your suite
pytest --shed --shed-image my-test-image --shed-image-policy rebuild

# Run tests without TestShed (default)
pytest
```
