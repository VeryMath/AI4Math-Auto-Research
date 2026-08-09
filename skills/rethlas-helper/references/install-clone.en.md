# Install and Remember Rethlas

Use this phase to resolve a remembered installation, locate an existing
repository, clone Rethlas, and save the machine-local installation path.

## 1. Read the installation record

Set `SKILL_DIR` to the directory containing the main `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" installation-show --json
```

`config_file` identifies the user-level configuration file and `rethlas_home`
identifies the remembered repository root. When both `configured` and `valid`
are `true`, set `TARGET` to that path.

When no installation is configured, use the destination supplied by the user
or ask where Rethlas should be installed. When a remembered path is invalid,
report the path and error, then ask for the moved repository or a new
destination.

## 2. Recognize a Rethlas repository

A valid repository root contains:

- `agents/generation/AGENTS.md`
- `agents/generation/.codex/config.toml`
- `agents/verification/AGENTS.md`
- `agents/verification/.codex/config.toml`

Inspect a selected directory:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor "$TARGET" --json
git -C "$TARGET" status --short
git -C "$TARGET" branch --show-current
git -C "$TARGET" remote -v
```

Report the repository structure, existing work, and origin. Preserve the
user's tracked and untracked files.

## 3. Obtain Rethlas

Use the repository URL selected by the user. The default upstream is:

```bash
git clone https://github.com/frenzymath/Rethlas.git "$TARGET"
```

Ask before the network operation. Use an empty destination or a path that has
not been created. Run the doctor again after cloning and confirm that the
directory is a recognized Rethlas root.

## 4. Save the installation path

After recognizing the repository root, run:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" installation-set "$TARGET" --json
```

The command writes the absolute path to:

```text
~/.config/opencode/rethlas-helper.toml
```

When `XDG_CONFIG_HOME` is set, the file is stored at
`$XDG_CONFIG_HOME/opencode/rethlas-helper.toml`.

Confirm resolution from another working directory:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor --json
```

OpenCode may request `external_directory` permission when a new project first
accesses the remembered repository. Explain the target path and keep the
approved scope on that Rethlas directory.

## Phase completion

Report:

- configuration file path;
- absolute `rethlas_home` path;
- repository origin and branch;
- doctor resolution from another working directory.

Continue to OpenCode environment configuration.
