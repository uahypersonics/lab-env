# lab-env

`lab-env` is a command-line tool for building consistent, inspectable research
computing environments on macOS and Linux. It keeps personal configuration in
one place and manages shell integration without replacing hand-written dotfiles.

## Features

- **Safe shell integration** for Bash and Zsh with preview, backup, status, and uninstall
- **Personal TOML configuration** stored outside the Python installation
- **Local diagnostics** for configuration, shell support, and SSH clients
- **Named host records** that reuse destinations and authentication from SSH configuration
- **Explicit config paths** for testing or maintaining separate environments

Connection commands, file transfers, navigation shortcuts, and site profiles
are planned but are not implemented yet.

## Quick Start

### Install

From a source checkout:

```bash
pip install -e .
```

See [Installation](installation.md) for supported Python versions, development
dependencies, and the future PyPI installation path.

### Initialize and Inspect

```bash
lab init
lab doctor
lab shell preview
```

### Install Shell Integration

After reviewing the preview:

```bash
lab shell install
source ~/.zshrc  # use ~/.bashrc for Bash
lab shell status
```

The installer adds one marked block to the startup file and writes generated
shell state under `~/.config/lab-env/`. It does not replace the dotfile or run
Python during normal shell startup.

Continue with [Getting Started](user-guide/getting-started.md) for the complete
first-run workflow, or see the [Command Reference](reference/commands.md) for
all available commands.

## Feedback & Contributing

Questions, bug reports, and contributions are welcome. Opening an issue is the
best first step when behavior is unclear or a workflow needs improvement:

- [Ask a question](https://github.com/uahypersonics/lab-env/issues/new?labels=question)
- [Report a bug](https://github.com/uahypersonics/lab-env/issues/new?labels=bug)
- [Suggest a feature](https://github.com/uahypersonics/lab-env/issues/new?labels=enhancement)

The repository [Contributing Guide](https://github.com/uahypersonics/lab-env/blob/main/CONTRIBUTING.md)
explains development setup, tests, documentation, and safety requirements.

## License

GNU General Public License v3.0 or later. See
[LICENSE](https://github.com/uahypersonics/lab-env/blob/main/LICENSE) for the
complete license terms.