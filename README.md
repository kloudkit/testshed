# KloudKIT TestShed

Integration tests need real services (a database, an API, a browser), not mocks.
Standing those up by hand means boilerplate container code in `conftest.py`,
flaky startup races, and leftover containers when a test crashes.

TestShed is a pytest plugin that hands you a running Docker container (or a
Playwright browser) as a fixture. You ask for `shed`, you get a live container;
the plugin builds or pulls the image, waits for readiness, and tears everything
down when the test ends.

## Features

- **Containers as fixtures:** request `shed` (or `docker_sidecar`) and run
  commands, read files, and inspect processes inside a real container.
- **Playwright browsers:** drive a browser running in a Playwright sidecar
  container.
- **Per-test configuration:** set env vars, volumes, and readiness probes with
  markers, or defaults for the whole suite via CLI.
- **Lifecycle handled:** images are resolved up front; containers and volumes are
  removed when the test finishes, even on failure.

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
whenever `--shed` is set, with no `conftest.py` import required.

## Usage

### Docker container testing

The `shed` fixture is the main entry point. By default it returns a **shared
container** (`shed_default`) reused across tests that don't override anything —
fast, because the container starts once. Apply a marker (env, volume, config, or
`@shed_mutable()`) and `shed` instead gives that test its own dedicated
container.

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
  # Picks up your configured defaults.
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
  # Container is NOT running yet; do setup here
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

#### Attach an existing container with `shed_attach`

Use `shed_attach` to pull an **already-running, externally-managed** container
into a test. The attached container exposes the full shed API (`.execute`, `.fs`,
`.proc`, `.ip()`, `.whoami()`, ...). For the duration of the test it is connected
to the shed network so it can reach the managed shed containers by name, and it is
disconnected when the test ends. It is **never removed** — the test does not own it.

```python
def test_against_running_service(shed_attach):
  db = shed_attach("my-postgres")

  assert db.execute("pg_isready")


def test_two_existing(shed_attach):
  db = shed_attach("my-postgres")
  cache = shed_attach("my-redis")


def test_managed_plus_existing(shed, shed_attach):
  external = shed_attach("legacy-app")

  # `shed` is a managed container; both share the shed network.
  assert shed.execute(["getent", "hosts", external.name])
```

The container must already be running, and the shed network must exist (i.e. do not
combine this with `--shed-skip-bootstrap`).

#### Basic Docker container

For a lower-level API, use the `docker_sidecar` fixture, which launches a
container directly from any image:

```python
def test_my_docker_app(docker_sidecar):
  nginx = docker_sidecar("nginx:latest", publish=[(8080, 80)])

  # The container's internal IP and current user.
  print(f"Container IP: {nginx.ip()}  user: {nginx.whoami()}")
```

#### Interacting with a container

Every container TestShed returns (`shed`, `docker_sidecar`, and friends) exposes
the same three helpers for poking at its runtime: `execute`, `fs`, and `proc`.

**`execute`: run commands.** Call it directly to use the container's default
shell, or pick one explicitly. Pass `raises=True` to fail the test on a non-zero
exit, and `user=` to run as another user:

```python
def test_commands(shed):
  # Default shell; output is returned stripped.
  assert shed.execute("echo hello") == "hello"

  # Specific shells.
  shed.execute.bash("set -o pipefail; cat /etc/os-release | head -1")
  shed.execute.sh(["echo", "portable"])
  shed.execute.zsh("print -r -- $ZSH_VERSION")

  # Raise on failure instead of returning, and run as a given user.
  shed.execute("test -f /etc/hostname", raises=True)
  assert shed.execute("whoami", user="nobody") == "nobody"
```

**`fs`: read the file system.** Check existence, list directories, and read
files as text, bytes, JSON, or YAML:

```python
def test_files(shed):
  assert shed.fs.exists("/etc/hostname")

  # List a directory (pass hidden=True to include dotfiles).
  assert "hostname" in shed.fs.ls("/etc")

  # Read contents. Calling fs directly is shorthand for fs.text(...).
  assert "root" in shed.fs("/etc/passwd")
  raw = shed.fs.bytes("/etc/hostname")
  config = shed.fs.json("/app/config.json")
  manifest = shed.fs.yaml("/app/manifest.yaml")

  # File mode (octal string), and ownership (user / group names).
  assert shed.fs.mode("/etc/hostname") == "644"
  assert shed.fs.owner("/etc/hostname") == "root"
  assert shed.fs.group("/etc/hostname") == "root"
```

**`proc`: inspect processes.** Check what's running by command name, resolve
PIDs, and read a process's command line or environment:

```python
def test_processes(shed):
  assert shed.proc.running("nginx")
  assert shed.proc.pids("nginx")  # tuple of matching PIDs

  # Command line of the first match.
  assert "nginx" in shed.proc.cmdline("nginx")

  # Environment of a process (PID 1 by default).
  assert shed.proc.environ()["PATH"]
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

To wait longer without restating the probe, pass `timeout=`; it overlays
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
| `downloader`              | function | `downloader(url, "filename") -> Path`: fetch a URL into a `tmp_path` file.                                                     |
| `test_root`               | session  | Absolute path to the tests root.                                                                                               |
| `project_root`            | session  | Absolute path to the project source root.                                                                                      |

### Command-line options

| Flag                         | Default                                | Description                                                                                                       |
| ---------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `--shed`                     | off                                    | Enable TestShed for the current test suite.                                                                       |
| `--shed-image IMAGE`         | —                                      | Base image repository (e.g. `ghcr.io/acme/app`). Must **not** contain a tag or digest; use `--shed-tag` for that. |
| `--shed-tag TAG\|SHA`        | `tests`                                | Image tag or digest (use a `sha256:...` for immutable builds).                                                    |
| `--shed-build-context DIR`   | project root (pytest config directory) | Docker build context for the `build` / `rebuild` policies.                                                        |
| `--shed-image-policy POLICY` | `pull`                                 | One of `pull`, `build`, `require`, `rebuild` (see below).                                                         |
| `--shed-src-dir DIR`         | `src`                                  | Project source directory, relative to the pytest config.                                                          |
| `--shed-stubs-dir DIR`       | `tests/stubs`                          | Directory of stub files (resolved by relative `@shed_volumes` sources).                                           |
| `--shed-tests-dir DIR`       | `tests`                                | Tests root directory.                                                                                             |
| `--shed-skip-bootstrap`      | off                                    | Skip Docker bootstrap (useful when running just the unit subset).                                                 |
| `--shed-container-logs`      | off                                    | Dump container logs on failure.                                                                                   |

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
# Rebuild the image, then run the suite against it.
pytest --shed --shed-image my-test-image --shed-image-policy rebuild

# Omit --shed and the plugin stays dormant: a plain pytest run.
pytest
```

### Parallel execution

`pytest -n auto` (pytest-xdist) works without extra setup. The Docker network
and container labels are namespaced by `PYTEST_XDIST_WORKER`, so workers don't
collide and each worker's containers are cleaned up independently.
