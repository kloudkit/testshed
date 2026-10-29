# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.23] - 2026-10-29

### Added

- ✨ Ship a TestShed Agent Skill, installable with `npx skills add kloudkit/testshed` or as a
  Claude Code plugin

### Changed

- ⬆️ Update the locked dependencies

### Fixed

- 🐛 Grant clipboard permissions to the pages and contexts `playwright_browser` creates,
  instead of to an unused context

## [0.0.22] - 2026-10-14

### Changed

- ⬆️ Update the locked dependencies, clearing the urllib3 and virtualenv advisories

## [0.0.21] - 2026-10-14

### Changed

- 🏷️ Use the GitHub tagline as the PyPI summary, and the repo topics as keywords
- 📝 Document `--shed-dockerfile` in the command-line options table

### Fixed

- 📜 Print an attached container's logs on failure with `--shed-container-logs`,
  as other shed containers do

## [0.0.20] - 2026-07-07

### Added

- 🐳 Build the shed image from a Dockerfile other than `Dockerfile` with
  `--shed-dockerfile`, under the `build` and `rebuild` policies and the `pull`
  fallback

## [0.0.19] - 2026-06-09

### Added

- 🔗 Pull an already-running, externally-managed container into a test with
  `shed_attach`; it joins the shed network for the test and is never removed

## [0.0.18] - 2026-06-04

### Added

- 📝 Document the container helpers, probes and fixtures in the README

### Fixed

- 🐛 Fail cleanly with `pytest.fail` when a filesystem or process helper hits a
  Docker error, instead of raising a confusing `AttributeError`

## [0.0.17] - 2026-06-03

### Added

- ⚙️ Inspect container processes with the `proc` helper

## [0.0.16] - 2026-06-01

### Fixed

- 🐛 Overlay probe settings onto any probe type, not just `HttpProbe`

## [0.0.15] - 2026-05-25

### Changed

- 🔼 Republish without code changes

## [0.0.14] - 2026-05-25

### Changed

- 🧼 Clean up and refactor the plugin internals

## [0.0.13] - 2026-03-09

### Added

- 🔎 Wait for readiness with `ShellProbe` and `LogProbe`, next to `HttpProbe`

## [0.0.12] - 2026-03-08

### Fixed

- 🐛 Let `probe=None` turn the default probe off, instead of being ignored

## [0.0.11] - 2026-03-08

### Changed

- 🧪 Extend the test suite

## [0.0.10] - 2026-03-08

### Added

- ⌚ Control when the container starts with the `shed_deferred` fixture

## [0.0.9] - 2026-02-24

### Added

- 🖨️ Print container logs when a test fails

## [0.0.8] - 2026-02-02

### Changed

- 🕶️ Manage the project with `uv`

## [0.0.7] - 2026-01-28

### Fixed

- ⭕ Reject a `--shed-image` that includes a tag or digest, and point to
  `--shed-tag` instead

## [0.0.6] - 2026-01-12

### Added

- 🗃️ Read a file's mode with the `fs.mode` helper

## [0.0.5] - 2025-12-01

### Changed

- 🔼 Republish without code changes

## [0.0.4] - 2025-10-27

### Fixed

- 🔧 Skip the session cleanup when TestShed is not enabled

## [0.0.3] - 2025-09-21

### Changed

- 🔧 Restructure the plugin architecture, without a global state object
- 🧼 Remove container labels after the test run

## [0.0.2] - 2025-09-17

### Added

- 🌐 Download remote files into a container with `RemoteVolume`

### Changed

- 🏳️ Select the image policy by name instead of with boolean flags
- 🚚 Move the packages to the `kloudkit.testshed` namespace, so editable
  installs work

### Fixed

- 🧼 Remove the Docker network after the test run
- 🧼 Print clean Docker error messages instead of the raw exception

## [0.0.1] - 2025-09-16

### Added

- 🐋 Provision Docker containers as pytest fixtures, with readiness probes and a
  container factory
- 💻 Pick a free host port for published ports

[Unreleased]: https://github.com/kloudkit/testshed/compare/v0.0.23...HEAD
[0.0.23]: https://github.com/kloudkit/testshed/releases/tag/v0.0.23
[0.0.22]: https://github.com/kloudkit/testshed/releases/tag/v0.0.22
[0.0.21]: https://github.com/kloudkit/testshed/releases/tag/v0.0.21
[0.0.20]: https://github.com/kloudkit/testshed/releases/tag/v0.0.20
[0.0.19]: https://github.com/kloudkit/testshed/releases/tag/v0.0.19
[0.0.18]: https://github.com/kloudkit/testshed/releases/tag/v0.0.18
[0.0.17]: https://github.com/kloudkit/testshed/releases/tag/v0.0.17
[0.0.16]: https://github.com/kloudkit/testshed/releases/tag/v0.0.16
[0.0.15]: https://github.com/kloudkit/testshed/releases/tag/v0.0.15
[0.0.14]: https://github.com/kloudkit/testshed/releases/tag/v0.0.14
[0.0.13]: https://github.com/kloudkit/testshed/releases/tag/v0.0.13
[0.0.12]: https://github.com/kloudkit/testshed/releases/tag/v0.0.12
[0.0.11]: https://github.com/kloudkit/testshed/releases/tag/v0.0.11
[0.0.10]: https://github.com/kloudkit/testshed/releases/tag/v0.0.10
[0.0.9]: https://github.com/kloudkit/testshed/releases/tag/v0.0.9
[0.0.8]: https://github.com/kloudkit/testshed/releases/tag/v0.0.8
[0.0.7]: https://github.com/kloudkit/testshed/releases/tag/v0.0.7
[0.0.6]: https://github.com/kloudkit/testshed/releases/tag/v0.0.6
[0.0.5]: https://github.com/kloudkit/testshed/releases/tag/v0.0.5
[0.0.4]: https://github.com/kloudkit/testshed/releases/tag/v0.0.4
[0.0.3]: https://github.com/kloudkit/testshed/releases/tag/v0.0.3
[0.0.2]: https://github.com/kloudkit/testshed/releases/tag/v0.0.2
[0.0.1]: https://github.com/kloudkit/testshed/releases/tag/v0.0.1
