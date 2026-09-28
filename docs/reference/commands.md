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

Validates configuration, reports whether the active shell is Bash or Zsh, checks
for a supported Conda initialization script, and locates `ssh`, `rsync`, `scp`,
and `sftp` on `PATH`. Missing clients or an enabled Conda integration without
`conda.sh` are warnings; invalid or missing configuration is an error.

## `lab connect HOST [REMOTE_ARGS]...`

Opens SSH to a configured host. Additional arguments run a remote command. Use
`--dry-run` to print the safely quoted command without starting a process. Use
`--` before remote arguments that begin with a hyphen.

## `lab pull HOST REMOTE_PATH [LOCAL_PATH]`

Pulls files with resumable rsync. The local path defaults to the current
directory. Archive mode, compression, partial files, append verification, and an
aggregate progress display are enabled. Use `--dry-run` to preview the command.

## `lab push HOST LOCAL_PATH REMOTE_PATH`

Pushes files with the same resumable rsync settings as `pull`. Local `~` paths
are expanded without changing trailing-slash semantics. Use `--dry-run` to
preview the command.

## `lab shell preview`

Prints the detected shell, startup paths, generated aliases and static state, and
managed blocks without writing files. Bash previews include `~/.bashrc` and the
login profile selected from `~/.bash_profile`, `~/.bash_login`, or `~/.profile`.
Use `--shell bash|zsh` and `--rc PATH` to override detection for inspection or
controlled tests.

## `lab shell install`

Validates personal configuration, writes generated shell setup to a static
fragment under `~/.config/lab-env/shell/`, and adds marked startup blocks.
For Bash, it installs into `.bashrc` and ensures the effective login profile also
loads it, unless that profile already sources `.bashrc`. Existing startup files
are backed up beside the original. Repeated installation is idempotent, and
symlinked startup files are rejected.

## `lab shell status`

Reports whether the managed startup blocks and generated shell file are present.

## `lab shell uninstall`

Backs up modified startup files, removes only lab-env-managed blocks, and deletes
the generated fragment. Other dotfile content is preserved.