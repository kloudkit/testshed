# Patterns

Complete tests for common cases.
Each one shows a rule from the skill in use; adapt the names, images and messages to the
project.

## Check the Image's Defaults

Read-only checks share one container, so they're fast; parametrize freely.

```python
import pytest


REQUIRED_PACKAGES = ["curl", "git", "unzip"]


def test_runs_as_app_user(shed):
  assert shed.execute("whoami") == "app"
  assert shed.fs.owner("/srv/app") == "app"


@pytest.mark.parametrize("package", REQUIRED_PACKAGES)
def test_package_installed(shed, package):
  shed.execute(f"command -v {package}")


def test_serves_home_page(shed):
  command = "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/"

  assert shed.execute(command) == "200"
```

`test_package_installed` asserts through `execute` alone: a missing package exits non-zero and
fails the test.

## Change the Container

```python
from kloudkit.testshed.docker.decorators import shed_mutable


@shed_mutable()
def test_cache_clear_removes_files(shed):
  shed.execute("touch /srv/app/cache/stale")
  shed.execute("app cache:clear")

  assert not shed.fs.exists("/srv/app/cache/stale")
```

## Configure the Startup

```python
from kloudkit.testshed.docker import InlineVolume
from kloudkit.testshed.docker.decorators import shed_env, shed_volumes


@shed_env(APP_PORT="8080", APP_DEBUG="true")
def test_debug_banner(shed):
  assert "Debug: true" in shed.logs()


@shed_volumes(
  ("config/app.yaml", "/etc/app/app.yaml"),
  InlineVolume("/etc/app/motd", "hello\n"),
)
def test_mounted_config(shed):
  assert shed.fs.yaml("/etc/app/app.yaml")["name"] == "demo"
  assert shed.fs("/etc/app/motd") == "hello\n"
```

The test with `@shed_env` restates `APP_PORT`: any marker drops the default `envs`.

## Talk to a Dependency

Start the dependency, then start the app pointed at its address:

```python
from kloudkit.testshed.docker import ShellProbe
from kloudkit.testshed.docker.decorators import shed_env


@shed_env(
  DB_CONNECTION="pgsql",
  DB_DATABASE="app",
  DB_USERNAME="app",
  DB_PASSWORD="secret",
)
def test_connects_to_postgres(docker_sidecar, shed_deferred):
  postgres = docker_sidecar(
    "postgres:16-alpine",
    envs={
      "POSTGRES_DB": "app",
      "POSTGRES_USER": "app",
      "POSTGRES_PASSWORD": "secret",
    },
    probe=ShellProbe(command="pg_isready -U app"),
  )

  app = shed_deferred(envs={"DB_HOST": postgres.ip()})

  assert "Database connection successful." in app.logs()
```

The same shape works for `redis:alpine`, `axllent/mailpit` *(SMTP on 1025)* or an S3 server.
Prepare the dependency with `execute` before starting the app when it needs data:

```python
@shed_env(FEATURE_STORE="redis")
def test_reads_feature_flag(docker_sidecar, shed_deferred):
  redis = docker_sidecar("redis:alpine", probe=ShellProbe(command="redis-cli ping"))
  redis.execute("redis-cli SET feature:beta on")

  app = shed_deferred(envs={"REDIS_HOST": redis.ip()})

  assert "beta: on" in app.execute("app features")
```

## Share a Costly Dependency

```python
import pytest

from kloudkit.testshed.docker import HttpProbe


@pytest.fixture(scope="module")
def web(docker_module_sidecar):
  return docker_module_sidecar(
    "nginx:1.27-alpine",
    volumes=[
      ("nginx.conf", "/etc/nginx/conf.d/default.conf"),
      ("certs", "/etc/nginx/certs"),
    ],
    probe=HttpProbe(port=80, command="wget -qO-"),
  )


def test_trusts_the_test_ca(shed_deferred, web):
  app = shed_deferred(
    volumes=[("certs/root.crt", "/usr/local/share/ca-certificates/test.crt")],
    add_hosts=[("web.test", web.ip())],
  )

  app.execute("curl -sf https://web.test")
```

This assumes an image that installs mounted CA certificates when it starts.
The module fixture starts nginx once for every test in the file.

## Expect a Startup Failure

`detach=False` runs the container to the end and returns its output.
A non-zero exit raises `DockerException`, so assert on it with `pytest.raises`:

```python
import pytest

from kloudkit.testshed.docker import DockerException
from kloudkit.testshed.docker.decorators import shed_env


@shed_env(DB_HOST="nonexistent-host", CONNECT_TIMEOUT="1")
def test_exits_without_database(shed_deferred):
  with pytest.raises(DockerException, match="Database connection failed"):
    shed_deferred(detach=False)
```

`match` searches the whole error, so it finds text the container wrote to stderr too.
To assert on more than one line, catch the error and check its text:

```python
from kloudkit.testshed.docker.decorators import shed_volumes


@shed_volumes(("hooks/fail.sh", "/app/hooks/pre-start/01-fail.sh"))
def test_failing_hook_stops_startup(shed_deferred):
  with pytest.raises(DockerException) as error:
    shed_deferred(detach=False)

  assert "Hook failed:" in str(error.value)
  assert "==> Starting" not in str(error.value)
```

`error.value.stdout` holds only the container's stdout; stderr isn't kept on the exception.

Keep timeouts in the image short through its env vars, so a failure test doesn't wait
minutes.

## Run a One-Shot Mode

```python
from kloudkit.testshed.docker.decorators import shed_env


@shed_env(APP_MODE="migrate")
def test_migrate_mode(shed_deferred):
  output = shed_deferred(detach=False)

  assert "==> Running migrations..." in output
```

## Wait for a Line, Then Assert

```python
from kloudkit.testshed.docker import LogProbe
from kloudkit.testshed.docker.decorators import shed_config, shed_volumes


HOOKS = (
  ("hooks/01-first.sh", "/app/hooks/pre-start/01-first.sh"),
  ("hooks/02-second.sh", "/app/hooks/pre-start/02-second.sh"),
)


@shed_volumes(*HOOKS)
@shed_config(probe=LogProbe(pattern=r"\[hook\] second"))
def test_hooks_run_in_order(shed_deferred):
  logs = shed_deferred().logs()

  assert logs.index("[hook] first") < logs.index("[hook] second")
```

Stub scripts must be executable on the host: mounts are read-only, so `chmod` inside the
container fails.

## Poll Mid-Test

When something changes after the container is up *(a restarted process, a reloaded config)*,
poll with a deadline instead of sleeping a fixed time:

```python
import time

import pytest


def wait_for(predicate, *, timeout=15.0, message="condition not met"):
  deadline = time.monotonic() + timeout

  while time.monotonic() < deadline:
    if predicate():
      return

    time.sleep(0.25)

  pytest.fail(f"{message} within {timeout}s")
```

```python
from kloudkit.testshed.docker.decorators import shed_mutable


@shed_mutable()
def test_supervisor_restarts_worker(shed):
  old = shed.proc.pids("worker")[0]
  shed.execute(f"kill -9 {old}")

  def restarted():
    pids = shed.proc.pids("worker")

    return bool(pids) and pids[0] != old

  wait_for(restarted, message="worker restart")
```

## Several Containers of the Image

```python
def test_replica_follows_primary(shed_deferred):
  primary = shed_deferred(envs={"ROLE": "primary"})
  replica = shed_deferred(envs={"ROLE": "replica", "PRIMARY_HOST": primary.ip()})

  assert "following primary" in replica.logs()
```

## A Container From Outside pytest

```python
def test_against_compose_db(shed, shed_attach):
  db = shed_attach("project-postgres-1")

  db.execute("pg_isready")
  shed.execute(["getent", "hosts", db.name])
```

## Drive the UI

```python
import pytest


@pytest.fixture
def browser_page(playwright_browser):
  page = playwright_browser.new_page()

  yield page

  page.close()


def test_login_page(shed, browser_page):
  page = browser_page
  page.goto(f"http://{shed.ip()}:8080/login")

  assert page.locator("input[name=password]").is_visible()
```

The browser runs in a container on the session's network, so it reaches `shed.ip()` directly.

## Unit Tests Beside Integration Tests

Keep tests that start no containers in their own directory and run them with
`--shed-skip-bootstrap`, so they need no image or network:

```sh
pytest tests/unit --shed-skip-bootstrap
pytest tests/integration -n auto
```
