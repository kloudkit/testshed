# Probes

A probe holds a container back until it's ready, so the test doesn't race its startup.
If it isn't ready in time, the test fails with what the probe waited for.

## Built-In Probes

Import them from `kloudkit.testshed.docker`.

| Probe                                       | Ready when                                         |
| ------------------------------------------- | -------------------------------------------------- |
| `HttpProbe(port=, endpoint=, host=, command=)` | `curl <host>:<port><endpoint>` exits 0 inside the container. |
| `LogProbe(pattern=)`                        | The regex matches the container's logs.            |
| `ShellProbe(command=)`                      | The command exits 0 inside the container.          |

- Every probe takes `timeout` *(seconds, 30 by default)* and retries every 100 ms.
- `HttpProbe` defaults to `host="http://localhost"` and `command="curl"`. Any HTTP status
  counts, because curl exits 0 on a 500. Use `command="curl -f"` to require a success, and
  `command="wget -qO-"` when the image has no curl.
- `LogProbe` searches with `re.search`: escape brackets and dots you mean literally.
- `ShellProbe` takes a string or a list and runs it like `execute`.

## Where Probes Go

```python
from kloudkit.testshed.docker import HttpProbe, ShellProbe
from kloudkit.testshed.docker.decorators import shed_config


@shed_config(probe=HttpProbe(port=8080, endpoint="/healthz"))
def test_app(shed):
  ...


def test_db(docker_sidecar):
  docker_sidecar(
    "postgres:16-alpine",
    envs={"POSTGRES_PASSWORD": "secret"},
    probe=ShellProbe(command="pg_isready -U postgres"),
  )
```

Set the probe for every `shed` container in `shed_container_defaults`.
A sidecar without a probe is handed over as soon as Docker starts it.

## Against the Default Probe

A probe passed to a test combines with the default one:

- **Same type:** the fields you set replace the default's. Fields you leave out keep the
  default's value when their own default is `None` *(`port`, `endpoint`)*; `timeout`, `host`
  and `command` come from the new probe. `HttpProbe(endpoint="/ready")` keeps the default's
  port, with a 30-second timeout.
- **Another type:** it replaces the default.
- **`probe=None`:** no probe for this container.
- **`timeout=` alone:** keeps the default probe and waits longer:

```python
@shed_config(timeout=90.0)
def test_slow_boot(shed):
  ...
```

`timeout` as a container argument works for `shed`, `shed_deferred` and `shed_factory`, not
for sidecars; set it on the sidecar's probe instead.

## Custom Probes

Subclass `Probe` with a `check` that raises until the container is ready and a
`failure_message` for the timeout:

```python
from dataclasses import dataclass

from kloudkit.testshed.docker import Probe


@dataclass(slots=True)
class FileProbe(Probe):
  path: str = "/tmp/ready"

  def check(self, container):
    container.execute(["test", "-e", self.path], raises=True)

  @property
  def failure_message(self):
    return f"{self.path} did not appear within {self.timeout}s"
```

Run commands in `check` with `raises=True`: without it, the first failed attempt fails the test
instead of retrying.
Keep the class a dataclass, so it merges with a default probe of the same type.

## When a Probe Times Out

The test fails with the probe's message, such as
`URL [http://localhost:8080/health] was not reachable within 30.0s`.
Rerun with `--shed-container-logs` to see what the container printed.
Common causes:

- The image has no `curl` for `HttpProbe`.
- The service listens on another port, or only on another interface.
- The container exited: a crash, or an image whose command finishes.
- A dedicated container lost an env var it needs, because markers drop the default `envs`.
