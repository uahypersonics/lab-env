# Configuration

Personal configuration uses TOML because it is readable, supports named tables,
and is parsed by Python 3.11 without executable configuration code.

## Schema

Every file declares a schema version. Version `1` rejects unknown fields so
misspellings produce errors instead of silently changing behavior.

```toml
schema_version = 1

[hosts.example]
destination = "example-ssh-alias"
description = "Fictitious documentation host"
```

Host `destination` values should normally name entries in `~/.ssh/config`.
Authentication, host keys, and usernames remain under SSH configuration rather
than being duplicated in `lab-env`.

The `[hosts]` table is for personal remote systems used by `connect`, `pull`, and
`push`. Shared destinations such as `uahpc` are provided by `lab-env` and work
without a local entry. Each `[hosts.NAME]` child table adds a host or overrides a
built-in entry, and the name is used on the command line.

The built-in `uahpc` SSH destination is `hpc.arizona.edu`; file transfers use
`filexfer.hpc.arizona.edu`. SSH uses the current local username unless you
specify `User` for that host in `~/.ssh/config`. For a personal host that uses a
different transfer endpoint, set `transfer_destination`:

```toml
[hosts.uahpc]
destination = "chader@hpc.arizona.edu"
# transfer_destination = "filexfer.hpc.arizona.edu"
```

When overriding a built-in host, unspecified built-in fields such as its
transfer destination remain in effect.

When a host requires a different SSH-compatible executable, configure its path
explicitly. `connect`, `pull`, and `push` all use the same executable:

```toml
[hosts.secure-cluster]
destination = "secure-cluster-ssh-alias"
description = "Fictitious secure HPC system"
ssh_command = "/opt/ossh/bin/ssh"
```

`ssh_command` must name one executable, not a shell command with embedded
options. Keep connection options, usernames, keys, and jump hosts in
`~/.ssh/config`.

The example is deliberately fictitious. Do not commit personal hostnames,
accounts, allocations, or credentials.

## Shell Aliases

The shell section controls aliases written to the generated Bash or Zsh fragment:

```toml
[shell]
initialize_conda = true
# conda_init_path = "/custom/conda/etc/profile.d/conda.sh"
default_aliases = true
disabled_aliases = ["rm"]

[shell.aliases]
gs = "git status"
project = 'cd "$HOME/work/current project"'
```

Default aliases provide `..`, `b`, `l`, `la`, `ll`, a platform-colorized `ls`, and
interactive `cp`, `mv`, and `rm` commands.

With `initialize_conda = true`, the generated shell file sources `conda.sh` from
common Miniforge, Miniconda, Anaconda, and Mambaforge installation locations.
This makes `conda activate` available but does not activate an environment.
Discovery checks an explicit `conda_init_path`, active Conda environment
variables, `conda info --base`, and common installation locations. Set
`conda_init_path` when Conda is installed in a custom or module-provided path.

Set `default_aliases = false` to disable all defaults, or list individual names in
`disabled_aliases`. Custom aliases are applied last, so they can add commands or
deliberately override a built-in alias. Alias names may contain letters, numbers,
`_`, `.`, and `-`; commands must be non-empty and single-line. Values are
interpreted by the active shell, so treat the personal configuration as executable
user input and do not copy untrusted commands into it.

## Managed Functions

Built-in functions are maintained separately from aliases in
`lab_env/shell/functions.py`, then rendered into the same generated Bash or Zsh
file. The startup file therefore needs only one managed source block.

`findbig` searches recursively from the current directory and defaults to files
larger than 100 MB. It passes matching paths directly from `find` to `du`, without
parsing `ls` output, so spaces in filenames are preserved.

`qs` lists your jobs using the scheduler available on the system: `squeue -u
"$USER"` for Slurm or `qstat -u "$USER"` for PBS. Additional arguments are
passed to the selected scheduler command.