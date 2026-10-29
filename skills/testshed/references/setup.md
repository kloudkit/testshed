# Setup

How to add TestShed to a project, configure the image it tests, and set suite-wide defaults.

## Install

```sh
pip install testshed            # or: uv add testshed --group dev
```

TestShed needs Python 3.11+, pytest 9+ and a Docker daemon, local or reachable through
`DOCKER_HOST`.
It installs `playwright` and `python-on-whales` with it.
Add `pytest-xdist` for parallel runs.

## Enable It

TestShed needs a pytest config file: it resolves its paths from that file's directory and names
the session after it.
Turn it on in `addopts`:

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--shed --shed-image=ghcr.io/acme/app --shed-tag=tests"
```

The plugin registers itself through its pytest entry point.
Don't add `pytest_plugins = ["kloudkit.testshed.fixtures"]` to `conftest.py`.

### A Separate Test Project

When the tests live beside a Dockerfile in another directory, give them their own config and
point the build context at the image:

```toml
# tests/pyproject.toml
[project]
name = "app-tests"
version = "0.0.0"
requires-python = ">=3.11"
dependencies = ["testshed"]

[tool.pytest.ini_options]
addopts = "--shed --shed-image=app --shed-image-policy=build --shed-build-context=.. --shed-stubs-dir=stubs --shed-container-logs"
```

## Images

`--shed-image` is the repository without a tag *(`ghcr.io/acme/app`)*.
It can't contain `:` or `@`, so a registry with a port *(`localhost:5000/app`)* is rejected.
`--shed-tag` is the tag *(`tests` by default)*, or a digest when it starts with `sha`.

`--shed-image-policy` decides how the image is acquired before the first test:

| Policy    | Behaviour                                                                 | Use it                        |
| --------- | ------------------------------------------------------------------------- | ----------------------------- |
| `pull`    | Local image if present, else pull, else build *(default)*.               | Day to day.                   |
| `build`   | Build only if the image isn't present locally.                            | Local images never pushed.    |
| `require` | Local image only; stop the session if it's missing.                       | CI, after a separate build.   |
| `rebuild` | Always build.                                                             | While changing the image.     |

Builds run `docker build --pull` with `Dockerfile` in the pytest config's directory.
`--shed-build-context` *(relative to the current directory)* and `--shed-dockerfile`
*(relative to the build context)* change that.

## Suite-Wide Defaults

Override `shed_container_defaults` in `conftest.py` to set what every `shed` container starts
with.
It must be session-scoped:

```python
import pytest

from kloudkit.testshed.docker import Container, HttpProbe


class AppContainer(Container):
  DEFAULT_USER = "app"
  DEFAULT_SHELL = "/bin/bash"


@pytest.fixture(scope="session")
def shed_container_defaults():
  return {
    "container_class": AppContainer,
    "probe": HttpProbe(port=8080, endpoint="/health"),
    "envs": {"APP_PORT": "8080"},
  }
```

Any `docker.run` argument works as a key, plus `probe`, `timeout` and `container_class`.
Markers apply on top of the defaults, key by key, with one exception: a dedicated container
takes `envs` and `volumes` from its markers alone, so default `envs` and `volumes` reach only
the shared container.

`container_class` also wraps containers from `shed_attach`.
`docker_sidecar` ignores the defaults.

## Custom Container Classes

| Attribute       | Default         | Effect                                            |
| --------------- | --------------- | ------------------------------------------------- |
| `DEFAULT_USER`  | `None`          | `user=` for every command.                        |
| `DEFAULT_SHELL` | `None` *(sh)*   | Shell for `execute(...)`.                         |
| `LOGIN_SHELL`   | `False`         | Run every command in a login shell *(`-cli`)*.    |
| `BASH_PATH`     | `/bin/bash`     | Shell for `execute.bash`.                         |
| `SH_PATH`       | `/bin/sh`       | Shell for `execute.sh`, and the default shell.    |
| `ZSH_PATH`      | `/usr/bin/zsh`  | Shell for `execute.zsh`.                          |

Add project helpers as methods on the subclass when several tests need them.

## Project Wrapper Fixtures

Name the fixtures after the thing under test when that reads better:

```python
import pytest


@pytest.fixture
def app(shed):
  return shed


@pytest.fixture
def app_factory(shed_deferred):
  return shed_deferred
```

Markers still apply: `app` is shared until the test carries a marker.

## A Derived Image

When the tests need more than the shipped image *(an app skeleton on a base image, test
tools)*, override `shed_tag` to build on top of it.
Every `shed` container then runs the derived image:

```python
import subprocess

import pytest


@pytest.fixture(scope="session")
def shed_tag(shed_state):
  tag = f"{shed_state.image}:test-derived"

  subprocess.run(
    [
      "docker",
      "build",
      "--build-arg",
      f"BASE_IMAGE={shed_state.image_and_tag}",
      "-t",
      tag,
      str(shed_state.tests_path),
    ],
    check=True,
  )

  return tag
```

```dockerfile
# tests/Dockerfile
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
RUN install-test-fixtures
```

`shed_state` holds the session's settings: `image`, `tag`, `image_and_tag`, `network`,
`labels`, `src_path`, `tests_path` and `stubs_path`.

## CI

Build and push the image in one job, then test it with `require` so the tests never rebuild
it:

```yaml
- run: docker pull ghcr.io/acme/app:pr-${{ github.event.pull_request.number }}

- run: pytest tests
  env:
    PYTEST_ADDOPTS: >-
      --shed-image-policy require
      --shed-tag pr-${{ github.event.pull_request.number }}
      --numprocesses 3
```

Run a unit-test subset that starts no containers with `--shed-skip-bootstrap`, so it needs no
image.
