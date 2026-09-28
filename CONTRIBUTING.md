# Contributing to lab-env

Contributions to code and documentation are welcome. Keep changes focused and
avoid including credentials, private hostnames, account names, allocation IDs,
or other personal infrastructure details.

## Development Setup

Clone the repository and install the package with development dependencies:

```bash
git clone https://github.com/uahypersonics/lab-env.git
cd lab-env
python -m pip install -e ".[dev]"
```

The supported baseline is Python 3.11. Continuous integration also tests Python
3.12 and 3.13 on Linux and macOS.

## Tests and Style

Run the same checks used by continuous integration:

```bash
pytest
ruff check .
ruff format --check .
```

Tests that exercise configuration or shell behavior must use temporary home and
configuration directories. Use fake client executables for connection tests.
Never alter real dotfiles, connect to real clusters, or transfer real data in an
automated test.

## Documentation

Build or preview the Zensical documentation locally:

```bash
zensical build --strict
zensical serve
```

Documentation changes should clearly distinguish implemented features from
planned behavior.

Package artifacts are built and checked by GitHub Actions. Publishing is
performed only through the release workflow: pushing a `vX.Y.Z` tag runs the
test suite, builds and checks both distributions, publishes them through PyPI
Trusted Publishing, and creates a GitHub Release. The package version is
derived from the tag by `setuptools-scm`. Do not add PyPI credentials or a
personal `.pypirc` to the repository.

## Pull Requests

Create a branch from `main`, include tests for behavioral changes, and open a
focused pull request. All contributions are made under the GNU General Public
License v3.0 or later.