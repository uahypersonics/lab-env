# lab-env

[![Tests](https://github.com/uahypersonics/lab-env/actions/workflows/test.yml/badge.svg)](https://github.com/uahypersonics/lab-env/actions/workflows/test.yml)
[![Documentation](https://github.com/uahypersonics/lab-env/actions/workflows/docs.yml/badge.svg)](https://uahypersonics.github.io/lab-env)
[![PyPI](https://img.shields.io/pypi/v/lab-env.svg)](https://pypi.org/project/lab-env/)
[![Python](https://img.shields.io/pypi/pyversions/lab-env.svg)](https://pypi.org/project/lab-env/)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-blue.svg)](LICENSE)

`lab-env` is a command-line toolkit for consistent research computing
environments on macOS and Linux. It keeps personal host configuration outside
the installed package and provides diagnostics without connecting to remote
systems or changing shell startup files.

## Status

The initial foundation implements:

- `lab init` to create personal TOML configuration safely;
- `lab hosts` to inspect configured SSH aliases;
- `lab doctor` to validate configuration, shell support, and local clients;
- `lab shell preview/install/status/uninstall` for managed Bash or Zsh startup integration;
- an explicit global `--config` option for isolated or alternate setups.

Connections, file transfers, navigation shortcuts, optional shell features, and
study orchestration are planned but are not implemented yet.

## Installation

Python 3.11 or newer is supported. For an isolated command-line installation,
use [pipx](https://pipx.pypa.io/):

```bash
pipx install lab-env
```

For development from a checkout:

```bash
python -m pip install -e ".[dev]"
```

## Quick Start

```bash
lab --help
lab init
lab hosts
lab doctor
lab shell preview
lab shell install
lab shell status
```

By default, configuration is stored at
`~/.config/lab-env/config.toml`. `XDG_CONFIG_HOME` is honored when set. Use an
explicit path for testing or multiple environments:

```bash
lab --config ./example.toml init
lab --config ./example.toml doctor
```

`lab init` refuses to overwrite an existing file. `lab shell install` is the
only current command that modifies shell startup configuration. Preview the
exact paths and managed block first with `lab shell preview`.

## Documentation

The user guide is available at
[uahypersonics.github.io/lab-env](https://uahypersonics.github.io/lab-env).
Development and contribution instructions are in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

`lab-env` is distributed under the
[GNU General Public License v3.0 or later](LICENSE).
