# Contributing

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Install dev dependencies with:

```bash
make install/dev
```

To install all dependencies including core and extras:

```bash
make install
```

### Dev and engine environments

Developer tools and the engine each keep their own environment:

| Environment | Location | Owner and purpose |
| --- | --- | --- |
| `.venv-dev` | Repository root | Developer tools: IDE interpreter, tests, linting and type checking. The `make install` targets create it. |
| `.venv` | Beside the library JSON | Runtime dependencies the engine installs from `pip_dependencies` when it loads the library. |
| `.venv-exec` | Beside the library JSON | Only if the library declares `pip_dependencies_exec`. The engine installs those and uses them only where nodes execute. |

The dev group includes `griptape-nodes-engine` and its dependencies. The engine puts the
library's `.venv` site-packages at the front of its import path, so if dev tooling lands there,
those copies shadow the running engine's own packages. The engine reports this as
`ShadowedEnginePackagesProblem` and loads the library as FLAWED. Keeping dev tooling in
`.venv-dev` keeps it off the engine's import path.

The Makefile sets `UV_PROJECT_ENVIRONMENT=.venv-dev`, so `make` targets use the right
environment. A plain `uv sync` or `uv run` installs into `.venv`, so set it yourself when you run
`uv` directly:

```bash
UV_PROJECT_ENVIRONMENT=.venv-dev uv run pytest
```

### Moving dev tooling out of `.venv`

If the `.venv` beside the library JSON holds dev tooling, from a plain `uv sync` or a Makefile
without the `.venv-dev` setting:

1. Run `make install/dev` from the repository root to create `.venv-dev`.
2. Select `.venv-dev` as your IDE's project interpreter (see below). Update any test, debug or
   run configuration that references `.venv` explicitly.
3. Close terminals with `.venv` activated, or run `deactivate` in them.
4. Stop Griptape Nodes and anything else using `.venv`, then delete that `.venv`.
   This removes every package installed there. Restart Griptape Nodes and let it rebuild the
   environment when it loads the library.
5. Run `make check` and `make test`. After registering the library in Griptape Nodes, check
   that no shadowing problem is reported.

An engine-managed `.venv` that holds only runtime dependencies can stay.

### PyCharm

1. Run `make install/dev` in the repository root.
2. Open **Settings > Project > Python Interpreter**. The exact labels vary by PyCharm version.
   Add an existing local interpreter and select `<repo>/.venv-dev/bin/python`. On Windows,
   select `<repo>\.venv-dev\Scripts\python.exe`.
3. Set test, debug and Python run configurations to use the project interpreter. Replace any
   explicit path to `.venv` with it.
4. Open a fresh terminal and check that any automatically activated environment is `.venv-dev`.

The Makefile's environment setting applies only to commands launched through Make. PyCharm's own
`uv sync` or `uv run` actions need `UV_PROJECT_ENVIRONMENT=.venv-dev` in their environment. If
your PyCharm version can't set that, install with `make install/dev` and keep the IDE pointed at
the `.venv-dev` interpreter.

### VS Code

1. Install the Microsoft Python extension and run `make install/dev` in the repository root.
2. Open the Command Palette and choose **Python: Select Interpreter**. Select `.venv-dev`, or
   choose **Enter interpreter path** and browse to `<repo>/.venv-dev/bin/python`. On Windows,
   select `<repo>\.venv-dev\Scripts\python.exe`.
3. Check `.vscode/launch.json` and `.vscode/tasks.json`, if present, for explicit `.venv` paths.
   Python debugging should use the selected interpreter or an explicit `.venv-dev` path. Shell
   tasks should call Make, or set `UV_PROJECT_ENVIRONMENT=.venv-dev` when invoking `uv`.
4. Close existing integrated terminals and open a new one so terminal activation picks up the
   selected interpreter. For the Testing panel, choose **Python: Configure Tests**, select
   pytest and use `tests` as the test directory.

Selecting `.venv-dev` as the interpreter doesn't redirect a plain `uv sync` or `uv run`; those
follow `UV_PROJECT_ENVIRONMENT`. Use Make targets, or set it for those commands.

## Makefile Targets

Run `make` with no arguments to see all available targets.

### Checks

Run all checks (format, lint, types) before submitting a PR:

```bash
make check
```

Individual checks:

```bash
make check/format   # ruff format --check
make check/lint     # ruff check
make check/types    # pyright
make check/json     # validate JSON files with jq
make check/changelog  # validate CHANGELOG.md and changelog.d entries
```

### Tests

```bash
make test
```

### Fixing Issues

Auto-fix formatting and linting issues:

```bash
make fix
```

### Dependency Sync

The `pip_dependencies` field in the library JSON is kept in sync with `pyproject.toml`. Run this after adding or removing dependencies:

```bash
make deps/sync
```

This is also run automatically as part of `make install/core` and `make install/all`.

## Changelog

[`CHANGELOG.md`](CHANGELOG.md) follows [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/), with one section per `library_version`.

A PR with a user-facing change does not edit `CHANGELOG.md`. It adds one file to [`changelog.d/`](changelog.d/README.md), named `<type>-<slug>.md` for one of `added`, `changed`, `deprecated`, `removed`, `fixed`, or `security`. The whole file is the bullet, with no heading above it. One entry per file keeps PRs from conflicting. `make changelog` prints the `[Unreleased]` section with every entry file folded in.

Write for the person updating the library: which node changed, what they will notice, and why. Link the GitHub issue on the entry's last line when there is one. Start breaking changes, anything that makes a saved workflow stop working or give a different result, with `**Breaking:**`. Refactors, tests, CI, and docs-only changes get no entry. The full style guide is in [CLAUDE.md](CLAUDE.md#changelog).

`make check/changelog`, part of `make check` and CI, validates the structure of `CHANGELOG.md` and of every entry file. It never requires a PR to add an entry. That call stays with people.

## CI

The CI workflow runs `make check` on every pull request and push to `main`. PRs must pass all checks before merging.

## Releases

Library versions follow [semantic versioning](https://semver.org/). The version is stored in two places, which the version targets keep in sync: the library JSON file under `metadata.library_version`, and `pyproject.toml` under `project.version`. The library JSON is the source of truth — `make version/get` reads it.

To check the current version:

```bash
make version/get
```

To set a specific version:

```bash
make version/set v=1.2.3
```

### Regular Release

1. Merge your changes to `main`.

2. Run **Actions > Version Bump (Patch)** or **Actions > Version Bump (Minor)** on `main`. This increments the version in the library JSON, folds the `changelog.d/` entries into a `CHANGELOG.md` section for the new version and deletes them, and commits both. It stops first if `CHANGELOG.md` or `changelog.d/` holds uncommitted changes, since the roll would overwrite them.

   Or bump locally and push:

   ```bash
   make version/patch   # 1.2.3 → 1.2.4
   make version/minor   # 1.2.3 → 1.3.0
   make version/major   # 1.2.3 → 2.0.0
   ```

3. Run **Actions > Version Publish** on `main`. This creates and pushes the version tag (e.g. `v1.2.3`), updates the `stable` tag, and creates a GitHub release with auto-generated release notes.

### Patch Release

To release a fix without including all commits on `main`, use a release branch:

1. Create a branch from the tag you want to patch:

   ```bash
   git checkout -b release/v0.50 v0.50.0
   git push -u origin release/v0.50
   ```

2. Cherry-pick the fix commit(s) you want to include:

   ```bash
   git cherry-pick <commit-sha>
   git push
   ```

3. Run **Actions > Version Bump (Patch)** and set the branch to `release/v0.50`.

4. Run **Actions > Version Publish** and set the branch to `release/v0.50`.
