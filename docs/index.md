# lab-env

`lab-env` is a command-line tool for setting up a consistent research computing environment on macOS and Linux.

## Quick Start

Install from PyPI:

```bash
pipx install lab-env
```

Initialize your config, check local tools, preview shell changes, then install:

```bash
lab init
lab doctor
lab shell preview
lab shell install
source ~/.zshrc  # use ~/.bashrc for Bash
```

The config is stored at `~/.config/lab-env/config.toml` by default. It includes
the shared `uahpc` host; use `lab connect uahpc` to connect, or add personal
hosts and aliases in the config. Shell integration writes a generated file under
`~/.config/lab-env/` and adds managed startup blocks without replacing your
existing dotfiles.

For more detail, see [Installation](installation.md), [Getting Started](user-guide/getting-started.md),
[Configuration](user-guide/configuration.md), and the [Command Reference](reference/commands.md).

## Help and Contributions

Report problems or ask questions in the
[GitHub issue tracker](https://github.com/uahypersonics/lab-env/issues). See the
[Contributing Guide](https://github.com/uahypersonics/lab-env/blob/main/CONTRIBUTING.md)
for development instructions.

## License

GNU General Public License v3.0 or later. See
[LICENSE](https://github.com/uahypersonics/lab-env/blob/main/LICENSE) for the
complete license terms.