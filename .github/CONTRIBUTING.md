# Contributing

Thanks for wanting to help.

1. Open an issue first for anything bigger than a small fix, so we can agree on
   the approach.
2. Install the hooks with `pre-commit install`.
3. Keep changes focused, and run
   `uv run pytest --shed --shed-image=debian --shed-tag=13` before opening a
   pull request.
4. Add a line to `CHANGELOG.md` under the unreleased version.
