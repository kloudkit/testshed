# Container API

Every container TestShed gives you, from `shed`, `shed_deferred`, `docker_sidecar` or
`shed_attach`, has the same helpers.
The image needs the tools they call: a shell, `test`, `ls`, `stat`, `grep`, `tr` and `cat`.

## `execute`

```python
shed.execute("echo hello")                  # "hello": output, trailing newline stripped
shed.execute(["echo", "hello"])             # a list is joined with spaces, unquoted
shed.execute("whoami", user="nobody")       # another user
shed.execute("pwd", workdir="/srv")         # any python-on-whales execute() argument
shed.execute("echo $HOME", envs={"HOME": "/x"})
shed.execute("source ~/.profile && env", login_shell=True)

shed.execute.bash("set -o pipefail; cat /etc/os-release | head -1")
shed.execute.sh(["echo", "portable"])
shed.execute.zsh("print -r -- $ZSH_VERSION")
```

- Commands run through `/bin/sh -c` *(or the class's `DEFAULT_SHELL`)*, so `$VAR`, pipes,
  `&&` and globs work and expand inside the container.
- A list is joined with spaces before the shell sees it. Quote values yourself with
  `shlex.quote`.
- A non-zero exit fails the test with the command's error output and no Python traceback.
  With `--shed-container-logs`, the container's logs are printed too.
- `raises=True` raises `DockerException` instead, to assert on or recover from:

```python
import pytest

from kloudkit.testshed.docker import DockerException


def test_missing_file(shed):
  with pytest.raises(DockerException, match="No such file"):
    shed.execute("cat /nope", raises=True)
```

- `check=False` returns a `Result` instead of failing, on `execute`, `.bash`, `.sh` and `.zsh`.
  Use it instead of `; echo exit=$?`, `|| true` or `2>&1` to read an exit code or stderr:

```python
def test_status(shed):
  result = shed.execute("grep -q nope /etc/hostname", check=False)

  assert result.exit_code == 1                  # also .ok, .stdout, .stderr
  assert shed.execute("echo w >&2", check=False).stderr == "w"
```

- `Result` streams lose their trailing newline, and `stderr` is kept on success too.
  Only `user`, `workdir` and `envs` are passed on, and a missing container still fails.

## `fs`

```python
shed.fs.exists("/etc/hostname")               # bool
shed.fs.ls("/etc")                            # tuple of names; hidden=True adds dotfiles
shed.fs("/etc/passwd")                        # text; same as shed.fs.text(...)
shed.fs.bytes("/etc/hostname")
shed.fs.json("/app/config.json")              # parsed
shed.fs.yaml("/app/manifest.yaml")            # parsed
shed.fs.toml("/app/pyproject.toml")           # parsed
shed.fs.mode("/etc/hostname")                 # "644"
shed.fs.owner("/etc/hostname")                # "root"
shed.fs.group("/etc/hostname")                # "root"
shed.fs.writable("/tmp", user="nobody")       # bool, as the command's user
```

`text`, `bytes`, `json`, `yaml` and `toml` copy the file out of the container, so they read paths
the container's user can't.
`exists`, `ls`, `mode`, `owner`, `group` and `writable` run commands as the container's user.

## `proc`

```python
shed.proc.running("nginx")                    # bool
shed.proc.pids("nginx")                       # tuple of PIDs
shed.proc.cmdline("nginx")                    # command line of the first match
shed.proc.environ()                           # dict, environment of PID 1
shed.proc.environ(42)                         # another PID
```

Names match the kernel's process name exactly, cut at 15 characters.
`cmdline` raises `LookupError` when nothing matches.
`environ` reads `/proc/<pid>/environ`, which holds nothing usable for a process that rewrites
its own title *(nginx does)*; read another PID, or `env()` for the exec environment.
To find a process by its full command line, use `pgrep -f` through `execute`.

## The Container Itself

- **`ip()`:** the container's address on the session's network, for other containers.
- **`whoami()`:** the user commands run as.
- **`env()` / `env(name)`:** the environment commands see *(dict, or one value, `None` when
  unset)*, including what the shell's profile exports. Use it instead of `echo $VAR`.
- **`logs()`:** the container's output so far, as one string.
- **`name`, `id`, `state`, …:** anything else goes to the python-on-whales container.
- **`wrapped`:** the python-on-whales container itself, with its exact type.

## Assert on Logs

`logs()` returns what the container printed so far.
A line that appears after the probe passed may not be there yet, so gate the container on it:

```python
from kloudkit.testshed.docker import LogProbe
from kloudkit.testshed.docker.decorators import shed_config


@shed_config(probe=LogProbe(pattern=r"==> Worker started"))
def test_worker_starts(shed_deferred):
  container = shed_deferred()

  assert "queue: default" in container.logs()
```

Strip colour codes before comparing when the image prints ANSI output.
