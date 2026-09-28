# Getting Started

This walkthrough initializes personal configuration, checks the local tools,
and installs the minimal managed shell block.

## 1. Initialize Personal Configuration

Run:

```bash
lab init
```

The command creates `~/.config/lab-env/config.toml`, or
`$XDG_CONFIG_HOME/lab-env/config.toml` when `XDG_CONFIG_HOME` is set. It refuses
to replace an existing file and does not alter shell startup files.

!!! tip
	Run `lab --config PATH init` to test with a temporary configuration or keep
	separate environments.

## 2. Check the Local Environment

Inspect the initialized configuration and required local clients:

```bash
lab hosts
lab doctor
```

`hosts` starts empty. `doctor` validates configuration, identifies Bash or Zsh,
and locates `ssh`, `rsync`, `scp`, and `sftp`. It never connects to a remote
system.

## 3. Connect and Transfer

After adding a host in `config.toml`, preview commands without connecting:

```bash
lab connect example --dry-run
lab pull example results/ ./results/ --dry-run
lab push example input/ work/input/ --dry-run
```

Remove `--dry-run` to execute them. Transfer paths preserve rsync's trailing
slash behavior: `results/` copies the directory contents, while `results` copies
the directory itself.

## 4. Preview Shell Integration

Before changing a startup file, inspect the exact paths and managed block:

```bash
lab shell preview
```

For Zsh, the preview normally resolves to:

- startup file: `~/.zshrc`
- generated file: `~/.config/lab-env/shell/zsh.sh`

For Bash, the startup file is `~/.bashrc`. Override detection when needed:

```bash
lab shell preview --shell bash
lab shell preview --shell zsh --rc ./temporary.zshrc
```

Preview does not write any files.

The generated-file preview includes the configured aliases. By default these are
the navigation/listing aliases `..`, `b`, `l`, `la`, `ll`, and colorized `ls`,
plus interactive `cp`, `mv`, and `rm` safety aliases. See
[Configuration](configuration.md#shell-aliases) to customize or disable defaults.

The same generated file contains managed shell functions. `findbig` recursively
lists files larger than 100 MB beneath the current directory. Pass a different
`find` size to change the threshold:

```bash
findbig
findbig 500M
findbig 2G
```

## 5. Install and Activate

```bash
lab shell install
source ~/.zshrc  # use ~/.bashrc for Bash
lab shell status
```

Installation:

1. Validates `config.toml`.
2. Creates a sibling backup such as `.zshrc.lab-env.bak`.
3. Adds one marked source block without replacing unrelated content.
4. Writes configured aliases, managed functions, and static state to one generated
   shell file under `~/.config/lab-env/shell/`.

Repeated installation does not duplicate the block. Normal shell startup is
quiet and does not launch Python or access the network.

## 6. Remove the Integration

Remove only the managed block and generated file with:

```bash
lab shell uninstall
```

The command backs up the startup file before editing and preserves all unrelated
content.

## Try the Workflow Safely

Run the complete workflow against temporary files instead of a real dotfile:

```bash
tmpdir=$(mktemp -d)
lab --config "$tmpdir/config.toml" init
lab --config "$tmpdir/config.toml" shell preview --shell zsh --rc "$tmpdir/.zshrc"
lab --config "$tmpdir/config.toml" shell install --shell zsh --rc "$tmpdir/.zshrc"
cat "$tmpdir/.zshrc"
```

See [Configuration](configuration.md) to add host records and the
[Command Reference](../reference/commands.md) for command details.