# Kloudkit TestShed

Kloudkit TestShed is a `pytest` plugin designed to streamline testing workflows by providing robust integration with Docker containers and Playwright. It simplifies the setup, execution, and teardown of test environments, allowing developers to focus on writing effective tests.

## Features

- **Automated Docker Management**: Easily spin up and manage Docker containers in tests.
- **Playwright Integration**: Run Playwright browser tests within isolated Docker.
- **Configurable via Markers and CLI**: Customize your test environment with flexibility.
- **Automated Resource Cleanup**: Ensures a clean state after test execution.

## Installation

```sh
pip install testshed
```

## Usage

### Docker Container Testing

TestShed provides `pytest` fixtures to manage Docker containers within your tests.

#### Basic Docker Container

You can use the `docker_sidecar` fixture to get a factory for creating Docker containers:

```python
import pytest

def test_my_docker_app(docker_sidecar):
    # Launch a simple Nginx container
    nginx_container = docker_sidecar("nginx:latest", publish=[(8080, 80)])

    # You can execute commands inside the container
    result = nginx_container.execute(["nginx", "-v"])
    assert "nginx version" in result

    # Access the container's IP
    ip_address = nginx_container.ip()
    print(f"Nginx container IP: {ip_address}")

    # Interact with the container's file system
    assert nginx_container.fs("/usr/share/nginx/html/index.html") == "Hello from TestShed!"
```

#### Configuring Containers with Decorators

You can configure your Docker containers using `pytest` markers:

- `@shed_config(**kwargs)`: Pass generic arguments to the Docker container.
- `@shed_env(**envs)`: Set environment variables for the container.
- `@shed_volumes(*mounts)`: Mount volumes into the container as `(source, dest)`.

```python
@shed_env(MY_ENV_VAR="hello")
@shed_volumes(("/path/to/host/data", "/app/data:ro"))
def test_configured_docker_app(docker_sidecar):
    my_app_container = docker_sidecar("my-custom-app:latest")
    # ... test logic ...
```

### Playwright Browser Testing

The `playwright_browser` fixture provides a Playwright browser instance running in a
Docker container, ready for your UI tests.

```python
def test_example_website(playwright_browser):
    page = playwright_browser.new_page()
    page.goto("http://example.com")
    assert "Example Domain" in page.title()
    # ... more Playwright test logic ...
```

### Command-Line Options

TestShed extends `pytest` with several command-line options to control the Docker
environment:

- `--shed-image IMAGE`: Specify the Docker image to use *(e.g., `ghcr.io/acme/app`)*.
- `--shed-tag TAG|SHA`: Specify the image tag or digest *(default: `tests`)*.
- `--shed-build-context DIR`: Set the Docker build context *(default: to `pytest.ini` directory)*.
- `--shed-require-local-image`: Fail if the image is not present locally *(no build or pull)*.
- `--shed-rebuild`: Force a rebuild of the test image.
- `--shed-network NAME`: Specify the Docker network to use *(default: `testshed-network`)*.
- `--shed-skip-bootstrap`: Skip Docker bootstrapping *(useful for unit tests)*.

Example usage:

```bash
pytest --shed-image my-test-image --shed-rebuild
```
