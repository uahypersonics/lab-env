# Installation

## Requirements

- Python 3.11 through 3.13
- macOS or Linux
- Bash or Zsh for shell integration

## From PyPI

Install the latest published release with pip:

```bash
pip install lab-env
```

For an isolated application install, use `pipx install lab-env`.

## From Source

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/uahypersonics/lab-env.git
cd lab-env
pip install -e .
```

## Development Installation

Install the test, lint, and documentation tools:

```bash
pip install -e ".[dev]"
pytest
```

The development extras include:

- [pytest](https://docs.pytest.org/) and pytest-cov for testing
- [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- [Zensical](https://zensical.org/) for local documentation builds

## Verify Installation

```bash
lab --version
lab --help
```

The command should be available from the environment where `lab-env` was
installed. Continue with [Getting Started](user-guide/getting-started.md).