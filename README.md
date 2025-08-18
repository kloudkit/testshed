# TestShed

> The support crew for your test bench.

## Overview

TestShed simplifies container-based testing with `pytest`.
It builds Docker images on demand, spins up sidecar services, and offers handy tools to
control them during your tests.

Highlights:

- Build and tag *test* images when you need them.
- Pytest fixtures to start and clean up temporary containers.
- Extensible building blocks: `Container`, `Factory`, `Probe`, etc.

## Usage

### CLI Flags

The TestShed `pytest` plugin adds several command-line options.
A typical
invocation might look like:

```bash
pytest --shed-rebuild --shed-image my/testshed-image --shed-network my-network
```

- **`--shed-rebuild`:** Force a rebuild of the Docker testing image *(default `True`)*.
- **`--shed-require-image`:** Fail if the testing image is not loaded locally *(default `False`)*.
- **`--shed-image`:** Docker image for testing *(default `testshed-image`)*.
- **`--shed-tag`:** Docker tag for the testing image *(default `tests`)*.
- **`--shed-network`:** Docker network to use when running containers *(default `testshed-network`)*.
- **`--shed-docker-context DIR`:** Docker build context *(relative to `pytest.ini`)*.
- **`--shed-src-dir DIR`:** Source root directory *(relative to `pytest.ini`, default `"src"`)*.
- **`--shed-stubs-dir DIR`:** Directory for test stubs *(relative to `pytest.ini`, default `"tests/stubs"`)*.
- **`--shed-tests-dir DIR`:** Tests root directory *(relative to `pytest.ini`, default `"tests"`)*.

### Fixtures

Several fixtures are available to help manage test resources:

```python
def test_example(docker_sidecar, shed_tag, project_root, test_root):
  container = docker_sidecar(image="redis:latest", publish=[(6379, 6379)])
  # interact with `container` or use `shed_tag`, `project_root`, `test_root`
```

Provided fixtures include:

- `docker_sidecar`, `docker_module_sidecar`, `docker_session_sidecar` for *(scoped)*
  lifecycle-managed containers.
- `shed_tag` giving the fully qualified image tag.
- `project_root` and `test_root` paths to your project and tests.
- `playwright_browser` to launch a connected Playwright browser.

### Exported classes

TestShed also exports classes for direct use:

```python
from kloudkit.testshed.docker import Container, Factory, Probe

import pytest


def redis():
  factory = Factory()
  yield factory("redis:latest", probe=Probe(port=6379))
  factory.clean()

@pytest.fixture
def redis_sidecar():
  return docker_sidecar("redis:latest", probe=Probe(port=6379))
```
