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