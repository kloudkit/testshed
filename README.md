# KloudKIT TestShed

A pytest plugin for integration testing with Docker and Playwright.
It handles container lifecycle, browser provisioning, and cleanup automatically.

## Features

- **Docker management:** provision and control containers from tests.
- **Playwright integration:** browser testing against a Playwright sidecar container.
- **Configurable via markers & CLI:** tune environments per test or suite.
- **Automatic cleanup:** containers and volumes are removed after tests.

## Requirements

- A running Docker daemon (local, or reachable via `DOCKER_HOST`).
- Python ≥ 3.11.
- pytest ≥ 9.

## Installation

```sh
pip install testshed
# or
uv add testshed --group dev
```

## Quick start

Enable TestShed via your pytest config:

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--shed --shed-image=ghcr.io/acme/app --shed-tag=tests"
```

Write a test against the auto-registered `shed` fixture:

```python
# tests/test_smoke.py
def test_container_is_alive(shed):
  assert shed.execute(["echo", "hello"]) == "hello"
```

Run it:

```sh
pytest
```

The fixtures (`shed`, `docker_sidecar`, `playwright_browser`, ...) are auto-registered
whenever `--shed` is set — no `conftest.py` import required.

## Usage

### Docker container testing

TestShed provides fixtures to manage containers inside your tests.

#### Configure containers with decorators

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

#### Readiness probes

A `probe` blocks until the container is ready, so tests don't race the startup
sequence. TestShed ships three:

```python
from kloudkit.testshed.docker import HttpProbe, LogProbe, ShellProbe

# Wait for an HTTP endpoint to respond.
HttpProbe(port=3000, endpoint="/health", timeout=30.0)

# Wait for a regex match in stdout/stderr.
LogProbe(pattern=r"ready to accept connections", timeout=30.0)

# Wait for a shell command to exit 0.
ShellProbe(command="pg_isready -U postgres", timeout=30.0)
```

Pass a probe wherever a container is created:

```python
@shed_config(probe=HttpProbe(port=8080, endpoint="/healthz"))
def test_app(shed):
  ...

def test_db(docker_sidecar):
  docker_sidecar(
    "postgres:16",
    envs={"POSTGRES_PASSWORD": "x"},
    probe=ShellProbe(command="pg_isready -U postgres"),
  )
```

You can also set a default for every `shed` container via the
`shed_container_defaults` fixture (`probe=...`).

To wait longer without restating the probe, pass `timeout=` — it overlays
onto the resolved probe, keeping the default's type and other fields:

```python
@shed_config(timeout=90.0)
def test_slow_boot(shed):
  ...
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

### Fixture reference

In addition to the headline fixtures (`shed`, `shed_deferred`, `docker_sidecar`,
`playwright_browser`), TestShed registers:

| Fixture                   | Scope    | Purpose                                                                                                                        |
| ------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `docker_module_sidecar`   | module   | Same factory as `docker_sidecar`, shared per test module.                                                                      |
| `docker_session_sidecar`  | session  | Same factory, shared across the whole session.                                                                                 |
| `shed_factory`            | function | Callable that builds a container with `shed_container_defaults` merged in; what `shed` and `shed_deferred` use under the hood. |
| `shed_container_defaults` | session  | Override in your own `conftest.py` to set image defaults (`container_class`, `envs`, `probe`, ...).                            |
| `shed_state`              | session  | Read-only access to the resolved `ShedState` (image, tag, network, paths).                                                     |
| `shed_tag`                | session  | Fully qualified `image:tag` (or `image@sha256:...`) used for the session.                                                      |
| `shed_default`            | session  | The shared default container that `shed` returns when no marker overrides apply.                                               |
| `downloader`              | function | `downloader(url, "filename") -> Path` — fetch a URL into a `tmp_path` file.                                                    |
| `test_root`               | session  | Absolute path to the tests root.                                                                                               |
| `project_root`            | session  | Absolute path to the project source root.                                                                                      |

### Command-line options

| Flag                         | Default                                | Description                                                                                                        |
| ---------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `--shed`                     | off                                    | Enable TestShed for the current test suite.                                                                        |
| `--shed-image IMAGE`         | —                                      | Base image repository (e.g. `ghcr.io/acme/app`). Must **not** contain a tag or digest — use `--shed-tag` for that. |
| `--shed-tag TAG\|SHA`        | `tests`                                | Image tag or digest (use a `sha256:...` for immutable builds).                                                     |
| `--shed-build-context DIR`   | project root (pytest config directory) | Docker build context for the `build` / `rebuild` policies.                                                         |
| `--shed-image-policy POLICY` | `pull`                                 | One of `pull`, `build`, `require`, `rebuild` (see below).                                                          |
| `--shed-src-dir DIR`         | `src`                                  | Project source directory, relative to the pytest config.                                                           |
| `--shed-stubs-dir DIR`       | `tests/stubs`                          | Directory of stub files (resolved by relative `@shed_volumes` sources).                                            |
| `--shed-tests-dir DIR`       | `tests`                                | Tests root directory.                                                                                              |
| `--shed-skip-bootstrap`      | off                                    | Skip Docker bootstrap (useful when running just the unit subset).                                                  |
| `--shed-container-logs`      | off                                    | Dump container logs on failure.                                                                                    |

> [!NOTE]
> When TestShed is installed globally, you must explicitly enable it per suite with
> `--shed`.
> This prevents it from configuring Docker in projects that don't use it.

#### Image policies

The `--shed-image-policy` option controls how TestShed acquires Docker images:

- **`pull`:** pull image if not found locally, build as fallback *(default)*.
- **`build`:** build only if image doesn't exist locally.
- **`require`:** require existing local image *(fails if not found)*.
- **`rebuild`:** always rebuild the image.

#### Examples

```sh
# Enable TestShed for your suite
pytest --shed --shed-image my-test-image --shed-image-policy rebuild

# Run tests without TestShed (default)
pytestpip install /workspace/kloudkit/testshed
```

### Parallel execution

`pytest -n auto` (pytest-xdist) is supported out of the box. The Docker network
and container labels are namespaced by `PYTEST_XDIST_WORKER`, so workers don't
collide and each worker's containers are cleaned up independently.
