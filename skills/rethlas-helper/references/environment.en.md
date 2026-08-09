# Configure the Rethlas OpenCode Environment

Use this phase to prepare the OpenCode CLI, the two Python environments, and
the provider/model selected by the user.

## 1. Resolve the remembered installation

Run:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor --json
```

Set `TARGET` to the reported `repository`. Report patch state, Python
environment state, and the OpenCode executable path.

## 2. Check base tools

```bash
git --version
python3 --version
uv --version
opencode --version
```

Use Python 3.12 or 3.13 for the Rethlas environments. Use `uv` to create the
environments and install dependencies.

Optional tools:

- `pdftotext` from Poppler for PDF references;
- Zola for the local proof result website.

Explain the related function and ask before a network installation.

## 3. Create generation and verification environments

Create one environment for each Rethlas agent:

```bash
uv venv "$TARGET/agents/generation/.venv" --python 3.13
uv pip install \
  --python "$TARGET/agents/generation/.venv/bin/python" \
  -r "$TARGET/agents/generation/mcp/requirements.txt"

uv venv "$TARGET/agents/verification/.venv" --python 3.13
uv pip install \
  --python "$TARGET/agents/verification/.venv/bin/python" \
  -r "$TARGET/agents/verification/requirements.txt"
```

When the system uses another supported Python version, replace `--python`
with the confirmed interpreter. Inspect the Python path and dependency imports
inside both environments.

## 4. Use the OpenCode provider and model

Inspect the user-level OpenCode configuration:

```bash
opencode auth list
opencode models
```

Guide the user through `/connect` in OpenCode when a provider connection is
needed. Let the user choose the provider, model, and variant. Rethlas stores
run artifacts in its repository, while OpenCode stores login information in
the user's OpenCode configuration.

Use the current OpenCode default model or a model id selected by the user:

```text
provider/model
```

Per-run model variables are:

```text
OPENCODE_GENERATION_MODEL
OPENCODE_VERIFICATION_MODEL
```

## 5. Inspect environment state

Confirm:

- the doctor resolves the intended `TARGET` from user configuration;
- both Python environments use the intended interpreter;
- generation MCP dependencies import successfully;
- verification API dependencies import successfully;
- OpenCode can read the user's provider and model list;
- optional Poppler and Zola availability matches the task.

A real model call consumes provider quota. State the selected model and ask
before the first call.

Continue to OpenCode compatibility installation.
