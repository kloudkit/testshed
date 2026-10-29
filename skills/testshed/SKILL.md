---
name: testshed
description: Write, fix and review pytest tests that run against real Docker containers and Playwright browsers with TestShed (the `testshed` package, imported as `kloudkit.testshed`). Use when a pytest config passes `--shed`, when tests use the `shed`, `shed_deferred`, `docker_sidecar`, `shed_attach` or `playwright_browser` fixtures or the `@shed_env`, `@shed_config`, `@shed_volumes` or `@shed_mutable` markers, or when asked to add container-based integration tests to a Python project.
license: MIT
compatibility: Needs Python 3.11+, pytest 9+, TestShed 0.0.22+ and a Docker daemon the test run can reach.
metadata:
  author: kloudkit
  homepage: https://testshed.kloudkit.com
---

# TestShed

TestShed is a pytest plugin that hands tests a running Docker container, or a Playwright
browser, as a fixture.
It gets the image, waits for the container to be ready and removes everything when the test
ends.

The full documentation is at <https://testshed.kloudkit.com>.
For anything this skill doesn't cover, fetch <https://testshed.kloudkit.com/llms.txt> (an index
of every page, each available as raw Markdown) or
<https://testshed.kloudkit.com/llms-full.txt> (every page in one file).

## Before You Write

1. Find the pytest config (`pyproject.toml` `[tool.pytest.ini_options]`, `pytest.ini`,
   `tox.ini` or `setup.cfg`) and read its `addopts`.
   TestShed does nothing without `--shed`, and needs `--shed-image`.
   If either is missing, set TestShed up first: see [setup](references/setup.md).
2. Read every `conftest.py` on the way to the test file.
   Note any `shed_container_defaults` override *(the default probe, envs and container class)*
   and any project fixture that wraps a TestShed one *(such as `app = shed`)*.
   Use the project's wrappers where they exist.
3. Find the stubs directory *(`--shed-stubs-dir`, `tests/stubs` by default)*: relative volume
   sources resolve against it.
4. Read two or three existing tests near the one you're writing and match their imports,
   naming and helpers.

## How TestShed Works

- **One image per session:** `--shed-image` *(no tag)* plus `--shed-tag` *(`tests` by
  default)*. TestShed pulls or builds it before the first test, as `--shed-image-policy` says.
- **One network per session:** every container TestShed starts joins it, so containers reach
  each other. Under pytest-xdist each worker gets its own.
- **Shared by default:** `shed` with no TestShed marker returns one container shared by the
  whole session *(`shed_default`)*, started with `shed_container_defaults`.
- **Dedicated on demand:** any TestShed marker on a test gives it its own container, removed
  when the test ends.
- **Ready before use:** a container with a probe isn't handed to the test until the probe
  passes.
- **Cleaned up:** everything TestShed starts is removed, even when a test fails.
  Containers brought in with `shed_attach` are never removed.

## Pick the Fixture

| The test needs to…                                      | Use                                                    |
| ------------------------------------------------------- | ------------------------------------------------------ |
| Check something without changing the container          | `shed`                                                 |
| Change the container *(write files, install, kill)*     | `shed` with `@shed_mutable()`                          |
| Start the image with other env vars, files or arguments | `shed` with `@shed_env`, `@shed_volumes`, `@shed_config` |
| Run setup first, or start several containers of the image | `shed_deferred(...)`                                 |
| Watch the container start and exit *(entrypoint, migrate, failures)* | `shed_deferred(detach=False)`             |
| Talk to a dependency *(database, cache, mail, S3)*       | `docker_sidecar(image, ...)`                           |
| Share a costly dependency across a module or session    | `docker_module_sidecar` / `docker_session_sidecar` in a fixture |
| Use a container started outside pytest                  | `shed_attach(name_or_id)`                              |
| Drive a web UI                                          | `playwright_browser`                                   |
| Get the image name for a container you start yourself   | `shed_tag`                                             |

Every fixture, scope and argument: [fixtures and options](references/fixtures-and-options.md).

## Configure the Container

Markers come from `kloudkit.testshed.docker.decorators`:

```python
from kloudkit.testshed.docker import HttpProbe, InlineVolume
from kloudkit.testshed.docker.decorators import shed_config, shed_env, shed_volumes


@shed_env(APP_ENV="testing", LOG_LEVEL="debug")
@shed_volumes(
  ("app.conf", "/etc/app/app.conf"),
  InlineVolume("/etc/app/extra.conf", "feature = on\n"),
)
@shed_config(probe=HttpProbe(port=8080, endpoint="/health"), user="app")
def test_app_reads_extra_config(shed):
  assert "feature = on" in shed.fs("/etc/app/extra.conf")
```

- **`@shed_env(**envs)`:** environment variables.
- **`@shed_volumes(*mounts)`:** `(source, dest)` tuples, `InlineVolume(path, content)` or
  `RemoteVolume(path, url)`, all mounted read-only.
- **`@shed_config(**kwargs)`:** anything python-on-whales' `docker.run` takes *(`publish`,
  `command`, `entrypoint`, `user`, `add_hosts`, …)*, plus `probe`, `timeout` and
  `container_class`.
- **`@shed_mutable()`:** a dedicated container with no other change.

`shed_deferred(...)` and `docker_sidecar(image, ...)` take the same settings as keyword
arguments *(`envs=`, `volumes=` and the rest)*.
With `shed_deferred`, call arguments merge onto the test's markers: `envs` merge with the
call winning, `volumes` are appended, anything else replaces the marker's value.

## Wait With Probes, Never `sleep`

```python
from kloudkit.testshed.docker import HttpProbe, LogProbe, ShellProbe

HttpProbe(port=8080, endpoint="/health")             # curl inside the container
LogProbe(pattern=r"ready to accept connections")     # regex over the container's logs
ShellProbe(command="pg_isready -U postgres")         # a command that exits 0
```

Each retries every 100 ms for up to `timeout` seconds *(30 by default)*.
Pass one as `probe=` wherever a container starts, or set it once in
`shed_container_defaults`.
`@shed_config(timeout=90)` waits longer without restating the default probe, and
`probe=None` turns it off.
Merge rules and custom probes: [probes](references/probes.md).

## Assert on the Container

```python
def test_service(shed):
  assert shed.execute("id -un") == "app"                # output, trailing newline stripped
  assert shed.fs.exists("/var/lib/app")
  assert shed.fs.mode("/etc/app/app.conf") == "644"
  assert shed.fs.json("/etc/app/manifest.json")["version"]
  assert shed.proc.running("nginx")
  assert "Listening on :8080" in shed.logs()
```

`execute` runs through `/bin/sh -c`; `execute.bash`, `.sh` and `.zsh` pick a shell, and
`user=` runs as another user.
Every container from every fixture has the same helpers: see
[container API](references/container-api.md).

## Rules

1. **Never change the shared container.** A bare `shed` is shared by every test in the
   session: writing files, installing packages or killing processes in it breaks other tests.
   Give the test a marker, `@shed_mutable()` at least.
2. **Don't stack `@shed_mutable()` with `@shed_env`.** It is an `@shed_env` underneath, and
   only one marker of each kind applies to a test. Any other marker already makes the
   container dedicated, so drop `@shed_mutable()`.
3. **The closest marker wins, whole.** A marker on a test replaces the same marker on its
   class or module *(`pytestmark`)*. Values are not merged, so restate what you still need.
4. **Dedicated containers drop the default `envs` and `volumes`.** A test with any marker, and
   every `shed_deferred` call, takes `envs` and `volumes` only from its own markers and
   arguments. Other defaults *(probe, container class)* still apply. Restate the env vars the
   image needs to start.
5. **A failed command fails the test.** `execute` exits the test on a non-zero status, with the
   command's error output, so a bare `shed.execute("test -f /x")` is already an assertion.
   To expect a failure, use `raises=True` inside `pytest.raises(DockerException, match=...)`.
   To read the output of a command that may fail, end it with `|| true`.
6. **Quote what you pass as a list.** A list is joined with spaces, unquoted, and run by the
   shell. Use `shlex.quote` for values with spaces or shell characters, or pass one string.
7. **Wait with a probe, not `time.sleep`.** If the test asserts on something that happens
   after startup, start the container with a `LogProbe` on that line *(often with
   `shed_deferred`)* and then assert. If you must wait mid-test, poll with a deadline and
   `pytest.fail` when it passes.
8. **Probes run inside the container.** `HttpProbe` needs `curl` in the image *(or
   `command="wget -qO-"`)* and accepts any HTTP status; `command="curl -f"` requires a
   success. A custom probe must call `execute(..., raises=True)`. In some images `localhost`
   resolves to `::1` first; for a service listening on IPv4 only, use `127.0.0.1`
   *(`HttpProbe(host="http://127.0.0.1", ...)`)*.
9. **Reach containers from containers.** Point one container at another with `other.ip()`
   *(or `other.name`)*. To check an HTTP endpoint, run `curl` inside a container with
   `execute`. The test process runs outside Docker's network, so `requests` against `ip()`
   fails on Docker Desktop and with a remote `DOCKER_HOST`.
10. **Mounts are read-only.** Relative sources resolve against the stubs directory; absolute
    ones stay as they are. To change a mounted file, copy it elsewhere inside a dedicated
    container. Prefer `InlineVolume` to a new stub file for a few lines of content.
11. **A sidecar must keep running.** An image whose default command exits *(`alpine`,
    `busybox`)* needs `command=["sleep", "infinity"]`. Don't set `name=`: parallel workers
    share the Docker daemon, and names collide.
12. **`detach=False` raises, it doesn't fail.** It runs the container to the end and returns
    its output; no probe runs. A non-zero exit raises `DockerException`: wrap it in
    `pytest.raises(DockerException, match=...)`, whose `match` searches the whole error,
    stderr included. The exception's `stdout` holds only what the container wrote to stdout.
13. **Session-scoped overrides stay session-scoped.** Overrides of `shed_container_defaults`
    and `shed_tag` must use `@pytest.fixture(scope="session")`.
14. **Parametrize on the shared container.** `@pytest.mark.parametrize` over a bare `shed` is
    free; with a TestShed marker each case starts a container. Put costly dependencies in a
    module-scoped fixture on `docker_module_sidecar`.
15. **Import from the public modules.** Use `kloudkit.testshed.docker` *(`Container`,
    `DockerException`, probes, volumes)* and `kloudkit.testshed.docker.decorators`
    *(markers)*. Don't import deeper modules, and don't add `pytest_plugins`: the plugin
    registers itself.
16. **Process names stop at 15 characters.** `proc.pids`, `proc.running` and `proc.cmdline`
    match the kernel's process name exactly, cut at 15 characters.

Worked examples of these rules: [patterns](references/patterns.md).

## Run and Verify

Run each test you write or change, and read the result.
If Docker isn't reachable from where you run, say so and don't report the tests as passing.

```sh
pytest tests/test_feature.py                               # addopts already carries --shed
pytest tests/test_feature.py -x --shed-container-logs      # print container logs on failure
pytest --shed-image-policy=rebuild                         # rebuild the image after changing it
pytest -n auto                                             # parallel, with pytest-xdist
```

- **A failed command or probe:** rerun with `--shed-container-logs`. A probe timeout says what
  it waited for, such as `URL [http://localhost:8080/health] was not reachable within 30.0s`.
- **A container to inspect:** while a session runs, `docker ps -a --filter
  label=com.kloudkit.testshed` lists its containers; `com.kloudkit.testshed.test` holds the
  test's node ID *(or `shed_default`)*.
- **Tests that start no containers:** `--shed-skip-bootstrap` skips the image and the network,
  so a unit-test subset runs without Docker. `shed_attach` doesn't work with it.
- **`--shed-image` rejected:** it takes no tag, digest or registry port; the tag goes in
  `--shed-tag` *(a value starting with `sha` is used as a digest)*.

## References

- [setup](references/setup.md): install, pytest config, image policies, suite-wide defaults,
  custom container classes, derived images and CI.
- [fixtures and options](references/fixtures-and-options.md): every fixture, marker, container
  argument and command-line option.
- [container API](references/container-api.md): `execute`, `fs`, `proc` and the container
  itself.
- [probes](references/probes.md): built-in probes, how they merge with the default, custom
  probes.
- [patterns](references/patterns.md): complete tests for common cases.
