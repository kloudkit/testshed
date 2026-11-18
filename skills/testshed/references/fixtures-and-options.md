# Fixtures and Options

Every fixture, marker, container argument and command-line option TestShed adds.
Fixtures and markers exist only when `--shed` is passed.

## Container Fixtures

| Fixture                  | Scope    | Returns                                                                       |
| ------------------------ | -------- | ----------------------------------------------------------------------------- |
| `shed`                   | function | The shared container, or a dedicated one when the test has a TestShed marker. |
| `shed_deferred`          | function | `shed_deferred(envs=…, volumes=…, **kwargs)`: starts a container when called. |
| `shed_attach`            | function | `shed_attach(name_or_id)`: wraps a running container you manage.              |
| `shed_default`           | session  | The shared container `shed` returns without markers.                          |
| `shed_factory`           | function | `shed_factory(**kwargs)`: starts a shed container, defaults merged in.        |
| `docker_sidecar`         | function | `docker_sidecar(image, **kwargs)`: starts a container from any image.         |
| `docker_module_sidecar`  | module   | Same as `docker_sidecar`, removed after the module.                           |
| `docker_session_sidecar` | session  | Same as `docker_sidecar`, removed after the session.                          |
| `playwright_browser`     | session  | A Playwright `Browser` connected to Chromium in a container.                  |

- **`shed_deferred`:** reads the test's markers, then merges the call: `envs` merge *(the call
  wins)*, `volumes` are appended, anything else replaces the `@shed_config` value of the same
  name. Every call starts a new container, so one test can start several.
- **`shed_factory`:** what `shed` and `shed_deferred` call underneath. It ignores markers and
  keeps the default `envs` and `volumes` unless you pass your own. Prefer `shed_deferred`
  unless you need exactly that.
- **`shed_attach`:** joins the container to the session's network for the test, so other
  containers reach it by name, and leaves it afterwards. It must already be running, is never
  stopped or removed, and needs the network, so it fails with `--shed-skip-bootstrap`.
- **`docker_sidecar`:** ignores `shed_container_defaults`. Use the module and session variants
  inside your own fixture of the same scope.
- **`playwright_browser`:** runs `mcr.microsoft.com/playwright` at the installed `playwright`
  package's version and connects to it on a published port at `127.0.0.1`, so the Docker
  daemon has to run where pytest runs, and the container has to reach the npm registry.
  One browser serves the session: open a page or context per test and close it.
  Pages and contexts it opens get `clipboard-read` and `clipboard-write` on top of any
  `permissions` you pass; `.wrapped` is the plain Playwright `Browser`.

## Settings and Paths

| Fixture                   | Scope    | Returns                                                                     |
| ------------------------- | -------- | --------------------------------------------------------------------------- |
| `shed_container_defaults` | session  | `{}`; override it to set defaults for every `shed` container.               |
| `shed_tag`                | session  | The image used, as `image:tag` or `image@sha256:…`; override to swap it.    |
| `shed_state`              | session  | The session's settings: image, tag, network, labels and paths.              |
| `test_root`               | session  | The tests directory, as an absolute path *(`--shed-tests-dir`)*.            |
| `project_root`            | session  | The source directory, as an absolute path *(`--shed-src-dir`)*.             |
| `downloader`              | function | `downloader(url, output)`: downloads into `tmp_path`, returns the `Path`.   |

`downloader` also takes `method`, `allow_redirects`, `raise_for_status` and
`request_options` *(passed to `requests`)*.

## Markers

Import them from `kloudkit.testshed.docker.decorators`.

| Marker                   | Effect                                                            |
| ------------------------ | ----------------------------------------------------------------- |
| `@shed_env(**envs)`      | Set environment variables.                                        |
| `@shed_volumes(*mounts)` | Mount `(source, dest)` tuples or volume objects, read-only.       |
| `@shed_config(**kwargs)` | Pass container arguments *(see below)*.                           |
| `@shed_mutable()`        | Give the test its own container, without other settings.          |

- Markers work on a test, a class or a module *(`pytestmark = [...]`)*.
- The closest one wins and replaces the others of its kind; values are not merged.
- Each kind applies once per test. `@shed_mutable()` is an `@shed_env` underneath.
- They affect `shed` and `shed_deferred`, not sidecars.

## Container Arguments

`docker_sidecar`, `shed_deferred`, `shed_factory` and `@shed_config` take any argument of
python-on-whales' `docker.run` *(`envs`, `publish`, `command`, `entrypoint`, `user`, `workdir`,
`add_hosts`, `init`, `tmpfs`, …)*, plus:

| Argument          | Description                                                                         |
| ----------------- | ----------------------------------------------------------------------------------- |
| `probe`           | A readiness probe to wait for; `None` for none.                                     |
| `timeout`         | Seconds to wait for the probe, keeping its other fields *(not on sidecars)*.        |
| `container_class` | The `Container` subclass to wrap the container in.                                  |
| `volumes`         | `(source, dest)` tuples or volume objects, mounted read-only.                       |
| `networks`        | Networks to join instead of the session's network.                                  |
| `detach`          | `False` runs the container to completion and returns its output.                    |

Containers always start with `remove=True` and the session's labels.

## Volumes

```python
from kloudkit.testshed.docker import InlineVolume, RemoteVolume

("nginx.conf", "/etc/nginx/nginx.conf")                       # stubs-relative source
("/etc/hostname", "/test/hostname")                           # absolute source
InlineVolume("/app/config.txt", "content", mode=0o644)        # text or bytes
RemoteVolume("/app/config.json", "https://example.com/c.json")  # downloaded first
```

`RemoteVolume` also takes `mode`, `method`, `allow_redirects`, `raise_for_status` and
`request_options`.
A directory works as a source too.

## Command-Line Options

Paths are relative to the pytest config's directory, except `--shed-build-context`, which is
relative to the current directory.

| Option                       | Default                       | Description                                                       |
| ---------------------------- | ----------------------------- | ----------------------------------------------------------------- |
| `--shed`                     | off                           | Enable TestShed.                                                  |
| `--shed-image IMAGE`         | none, required                | Image repository, without a tag.                                  |
| `--shed-tag TAG\|SHA`        | `tests`                       | Image tag, or a digest when it starts with `sha`.                 |
| `--shed-image-policy POLICY` | `pull`                        | `pull`, `build`, `require` or `rebuild`.                          |
| `--shed-build-context DIR`   | the pytest config's directory | Build context for builds.                                         |
| `--shed-dockerfile FILE`     | `Dockerfile`                  | Dockerfile, relative to the build context.                        |
| `--shed-src-dir DIR`         | `src`                         | Source directory, for `project_root`.                             |
| `--shed-tests-dir DIR`       | `tests`                       | Tests directory, for `test_root`.                                 |
| `--shed-stubs-dir DIR`       | `tests/stubs`                 | Where relative volume sources resolve.                            |
| `--shed-skip-bootstrap`      | off                           | Skip the image and network, for tests that start no containers.   |
| `--shed-container-logs`      | off                           | Print container logs when a command or probe fails a test.        |

## Labels

| Label                        | Value                                                                  |
| ---------------------------- | ---------------------------------------------------------------------- |
| `com.kloudkit.testshed`      | The session *(`testshed-<project>-<random>[-gwN]`)*, also the network name. |
| `com.kloudkit.testshed.test` | The pytest node ID of the test that started a `shed` container, or `shed_default`. |
