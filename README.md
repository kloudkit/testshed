# KloudKIT TestShed

> Meet **KloudKIT TestShed**, a tidy home for your integration-testing power tools.
>
> It snap-fits into `pytest`, auto-provisions Docker, runs Playwright, and cleans up after itself
> so you can focus on building sharp tests.

## Features

- **Automated Docker management:** Spin up and control containers from tests.
- **Playwright integration:** Run browser tests in isolated Docker environments.
- **Configurable via markers & CLI:** Tune environments per test or suite.
- **Automatic resource cleanup:** Ensures a clean state after tests.

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

#### High-level `shed` fixtures

Use the `shed` fixture for smart container management with configurable defaults:

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

You can also use the factory directly:

```python
def test_custom_setup(shed_factory):
  container = shed_factory(envs={"CUSTOM_VAR": "value"})
  # ... test logic ...
```

#### Basic Docker container

For a lower-level API, use the `docker_sidecar` fixture to create containers:

```python
import pytest

def test_my_docker_app(docker_sidecar):
  # Launch a simple Nginx container
  nginx = docker_sidecar("nginx:latest", publish=[(8080, 80)])

  # Execute a command inside the container
  assert "nginx version" in nginx.execute(["nginx", "-v"])

  # Access the container's IP
  print(f"Nginx container IP: {nginx.ip()}")

  # Interact with the file system
  assert "/usr/share/nginx/html" in nginx.fs.ls("/usr/share/nginx")
```

#### Configure containers with decorators

Configure containers using `pytest` markers/decorators:

- **`@shed_config(**kwargs)`:** Generic container args.
- **`@shed_env(**envs)`:** Environment variables.
- **`@shed_volumes(*mounts)`:** Volume mounts as `(source, dest)` or `BaseVolume`.
- **`@shed_mutable()`:** Force non-default shed for tests that perform mutable operations.

```python
from kloudkit.testshed.docker import InlineVolume, RemoteVolume

@shed_env(MY_ENV_VAR="hello")
@shed_volumes(
  ("/path/to/host/data", "/app/data"),
  InlineVolume("/app/config.txt", "any content you want", mode=0o644),
  RemoteVolume("/app/remote-config.json", "https://api.example.com/config.json", mode=0o644),
)
def test_configured_docker_app(shed):
  # ... test logic ...
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

- **`--shed`:** Enable TestShed for the current test suite *(default: disabled)*.
- **`--shed-image IMAGE`:** Base image *(e.g., `ghcr.io/acme/app`)*.
- **`--shed-tag TAG|SHA`:** Image tag or digest *(default: `tests`)*.
- **`--shed-build-context DIR`:** Docker build context *(default: `pytest.ini` directory)*.
- **`--shed-image-policy POLICY`:** Image acquisition policy for building or pulling *(default: `pull`)*.
- **`--shed-skip-bootstrap`:** Skip Docker bootstrapping *(useful for unit tests)*.

> [!NOTE]
> When TestShed is installed globally, you must explicitly enable it per suite with
> `--shed`.
> This prevents it from configuring Docker in projects that don't use it.

#### Image Policies

The `--shed-image-policy` option controls how TestShed acquires Docker images:

- **`pull`** *(default)***:** Pull image if not found locally, build as fallback.
- **`build`:** Build only if image doesn't exist locally.
- **`require`:** Require existing local image *(fails if not found)*.
- **`rebuild`:** Always rebuild the image.

#### Examples

```bash
# Enable TestShed for your suite
pytest --shed --shed-image my-test-image --shed-image-policy rebuild

# Run tests without TestShed (default)
pytest
```
