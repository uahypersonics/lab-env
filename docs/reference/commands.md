# Command Reference

## Global Options

`lab --config PATH COMMAND` selects a personal configuration file.
`lab --version` prints the installed version.

## `lab init`

Creates the selected configuration and parent directories. Existing files are
preserved and produce a nonzero exit code. No dotfiles are modified.

## `lab hosts`

Validates configuration and lists host names, SSH destinations, and optional
descriptions. It does not connect to a host.

## `lab doctor`

Validates configuration, reports whether the active shell is Bash or Zsh, and
locates `ssh`, `scp`, and `sftp` on `PATH`. Missing clients are warnings; invalid
or missing configuration is an error.

## `lab shell preview`

Prints the detected shell, startup path, generated static file, and exact managed
block without writing files. Use `--shell bash|zsh` and `--rc PATH` to override
detection for inspection or controlled tests.

## `lab shell install`

Validates personal configuration, writes a static shell fragment under
`~/.config/lab-env/shell/`, and adds one marked source block to `.bashrc` or
`.zshrc`. Existing startup files are backed up beside the original. Repeated
installation is idempotent, and symlinked startup files are rejected.

## `lab shell status`

Reports whether the managed block and generated shell file are both present.

## `lab shell uninstall`

Backs up the startup file, removes only the marked block, and deletes the
generated fragment. Other dotfile content is preserved.