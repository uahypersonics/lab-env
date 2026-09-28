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

The example is deliberately fictitious. Do not commit personal hostnames,
accounts, allocations, or credentials.