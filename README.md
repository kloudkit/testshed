# KloudKIT TestShed

`KloudKIT TestShed` is a `pytest` plugin that streamlines integration tests with Docker
containers and Playwright—handling setup, execution, and teardown so you can focus on
writing effective tests.

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
- **`@shed_volumes(*mounts)`:** Volume mounts as `(source, dest)` or `InlineVolume`.

```python
from kloudkit.testshed.docker import InlineVolume

@shed_env(MY_ENV_VAR="hello")
@shed_volumes(
  ("/path/to/host/data", "/app/data:ro"),
  InlineVolume("/app/config.txt", "any content you want", mode=0o644),
)
def test_configured_docker_app(docker_sidecar):
  app = docker_sidecar("my-custom-app:latest")
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

- `--shed`: Enable TestShed for the current test suite *(default: disabled)*.
- `--shed-image IMAGE`: Base image *(e.g., `ghcr.io/acme/app`)*.
- `--shed-tag TAG|SHA`: Image tag or digest *(default: `tests`)*.
- `--shed-build-context DIR`: Docker build context *(default: `pytest.ini` directory)*.
- `--shed-require-local-image`: Fail if image isn’t present locally *(no build/pull)*.
- `--shed-rebuild`: Force rebuilding the test image.
- `--shed-network NAME`: Docker network *(default: `testshed-network`)*.
- `--shed-skip-bootstrap`: Skip Docker bootstrapping *(useful for unit tests)*.

> [!NOTE]
> When TestShed is installed globally, you must explicitly enable it per suite with
> `--shed`.
> This prevents it from configuring Docker in projects that don’t use it.

#### Examples

```bash
# Enable TestShed for your suite
pytest --shed --shed-image my-test-image --shed-rebuild

# Run tests without TestShed (default)
pytest
```
