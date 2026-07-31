# Manage the OpenCode Compatibility Patch

Read this reference only after the user explicitly chooses OpenCode support,
or when the user asks to inspect, update, or remove an existing installation.

## Contents

1. What the patch does
2. Preflight
3. Install
4. Validate
5. Remove
6. Report

## What the patch does

The bundled patch is a standard Git patch against upstream commit
`974b82ccfbcb07c405a233886e6e8d1d4db84828`. It adds nine OpenCode-only files:

- English and Simplified Chinese OpenCode guides;
- generation and verification `opencode.json` files;
- OpenCode-specific `AGENTS` instructions;
- an OpenCode generation runner;
- an OpenCode verification API;
- an OpenCode recursive-proving skill.

It does not edit the original Codex files. Codex commands continue to work
after installation. It also does not bundle a provider, model, variant, API
key, or other credential; OpenCode uses the user's own configuration.

## Preflight

Run:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-status "$TARGET"
git -C "$TARGET" status --short
git -C "$TARGET" branch --show-current
git -C "$TARGET" rev-parse HEAD
```

Preserve unrelated work. Apply only on a user-approved non-default branch;
create or switch branches when needed. Do not stage or commit unless the user
also requested it.

Stop when:

- any manifest path already exists with unrelated content;
- the repository contains a partial patch installation;
- `git apply --check` fails;
- the branch choice is unresolved.

## Install

Use the idempotent helper:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-apply "$TARGET"
```

The helper validates the packaged checksum and applicability before writing.
A newer upstream revision is acceptable only when the applicability check
succeeds.

For direct inspection, the assets are:

```text
assets/rethlas-opencode-compat.patch
assets/rethlas-opencode-compat.json
```

Do not use `--reject`, overwrite conflicts, or manually copy only part of the
manifest.

## Validate

Run the status command again and confirm `patch_state: installed`. Then check:

```bash
python3 -m json.tool "$TARGET/agents/generation/opencode.json"
python3 -m json.tool "$TARGET/agents/verification/opencode.json"
bash -n "$TARGET/agents/generation/tests/run_example_opencode.sh"
```

With OpenCode configured, inspect agents and MCP servers from the appropriate
directories:

```bash
opencode agent list
opencode mcp list
```

Confirm that original tracked files have no diff. The installed usage guides
are:

- `README.opencode.md`
- `README.opencode.zh-CN.md`

Before a first run, guide the user through `opencode auth list`, `/connect`,
and `opencode models`. Let the user choose their coding plan or API provider
and model. Do not insert a fallback model into project files or launch
scripts.

Ask before any model-backed smoke test.

## Remove

Removal is safe only while all nine files still match the patch:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-remove "$TARGET"
```

The helper performs a reverse applicability check and refuses to delete a
modified file. Report conflicts instead of forcing removal.

## Report

Report the patch state, branch, `HEAD`, checksum result, conflicts, validation
results, and whether the user selected Codex, OpenCode, or both for subsequent
usage guidance.
