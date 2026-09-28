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

Prints the detected shell, startup path, generated aliases and static state, and
exact managed block without writing files. Use `--shell bash|zsh` and `--rc PATH`
to override detection for inspection or controlled tests.

## `lab shell install`

Validates personal configuration, writes configured aliases to a static shell
fragment under `~/.config/lab-env/shell/`, and adds one marked source block to
`.bashrc` or `.zshrc`. Existing startup files are backed up beside the original.
Repeated installation is idempotent, and symlinked startup files are rejected.

## `lab shell status`

Reports whether the managed block and generated shell file are both present.

## `lab shell uninstall`

Backs up the startup file, removes only the marked block, and deletes the
generated fragment. Other dotfile content is preserved.