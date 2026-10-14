# Contributing

Thanks for wanting to help.

1. Open an issue first for anything bigger than a small fix, so we can agree on
   the approach.
2. Install the hooks with `pre-commit install`.
3. Keep changes focused, and run
   `uv run pytest --shed --shed-image=debian --shed-tag=13` before opening a
   pull request.
4. Add a line to `CHANGELOG.md` under the unreleased version.

## Releasing

1. In `CHANGELOG.md`, rename `## [Unreleased]` to `## [X.Y.Z] - YYYY-MM-DD`,
   add a new empty `## [Unreleased]` above it, and update the links at the
   bottom.
2. Set `__version__` in `src/kloudkit/testshed/__init__.py` to `X.Y.Z`.
3. Commit as `🔖 Release vX.Y.Z` and push to `main`.
4. Tag and push the tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.

The tag runs CI, then publishes the package to PyPI and creates the GitHub
Release, with the CHANGELOG section as its notes. It stops before publishing
anything if that section is missing, or if `__version__` doesn't match the tag.
