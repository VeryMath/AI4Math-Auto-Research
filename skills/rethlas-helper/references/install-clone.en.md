# Install or Clone Rethlas

Use this reference only for locating or obtaining the repository. Leave
Python environments, provider login, the OpenCode patch, and first-run
commands to their own phases.

## 1. Resolve paths

Set `SKILL_DIR` to the directory containing the main `SKILL.md`. Set `TARGET`
to the intended Rethlas repository root.

If the user did not provide `TARGET`, search the current workspace first. A
valid root contains all four paths:

- `agents/generation/AGENTS.md`
- `agents/generation/.codex/config.toml`
- `agents/verification/AGENTS.md`
- `agents/verification/.codex/config.toml`

## 2. Inspect an existing repository

Run:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor "$TARGET"
```

Also inspect:

```bash
git -C "$TARGET" status --short
git -C "$TARGET" branch --show-current
git -C "$TARGET" rev-parse HEAD
git -C "$TARGET" remote -v
```

Preserve all unrelated tracked and untracked files. If the directory is not a
valid Rethlas repository, report which required paths are missing before
offering to clone elsewhere.

## 3. Clone when no installation exists

Use the repository requested by the user. Otherwise use the official upstream:

```bash
git clone https://github.com/frenzymath/Rethlas.git "$TARGET"
```

Cloning requires network access, so ask before running it. Do not replace a
non-empty target directory.

After cloning, record:

- absolute repository path;
- origin URL;
- current branch and `HEAD`;
- whether the doctor recognizes the repository.

## Phase boundary

Stop the installation phase once the repository is present and valid. Move to
the environment phase for CLIs, Python environments, authentication, and
runtime checks. Do not install the OpenCode patch during this phase.
