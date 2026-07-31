# Configure the Rethlas Environment

Guide the user through this checklist instead of presenting an undifferentiated
command dump. Explain what each component enables, inspect existing state, and
install only what the selected workflow needs.

## Contents

1. Confirm runtime selection
2. Check base tools
3. Create the two Python environments
4. Configure Codex when selected
5. Configure OpenCode when selected
6. Validate without a model call
7. Respect the phase boundary

## 1. Confirm runtime selection

Upstream Rethlas is based on Codex. Check whether the Codex CLI is usable:

```bash
command -v codex
codex --version
```

Follow the conditional selection gate in the main `SKILL.md`:

- without Codex, explain the dependency and ask whether to install the
  OpenCode patch;
- with Codex, ask whether to use original Rethlas directly or install the
  OpenCode patch as an additional runtime;
- with an existing patch, ask which installed runtime to configure.

Do not choose OpenCode merely because Codex is absent, and do not select a
provider or model on the user's behalf.

Run the doctor first:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor "$TARGET"
```

Summarize what already exists before proposing changes.

## 2. Check base tools

Check:

```bash
git --version
python3 --version
uv --version
```

Prefer an installed Python 3.12 or 3.13. Use `uv` when available; otherwise
use `python3 -m venv` and `pip`.

Optional tools:

- `pdftotext` from Poppler for PDF reference extraction;
- Zola for the local result website;
- Node/npm only when required to install Codex.

Explain the related feature before offering an optional installation. Ask
before any network-backed installation.

## 3. Create the two Python environments

Rethlas separates proof generation from verification. Create both
environments even when they use the same Python installation:

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

Without `uv`, create each `.venv`, activate it, and install the corresponding
requirements file with `pip`. Keep environments inside their existing ignored
runtime directories.

Verify imports or package metadata with each environment's Python. Do not
claim readiness merely because the directories exist.

## 4. Configure Codex when selected

Check the CLI and user-level login separately:

```bash
codex --version
codex login status
```

If the CLI is missing, inspect current upstream/official instructions before
installing. The checked-out Rethlas README may document:

```bash
npm install -g @openai/codex
```

Do not edit project `.codex` files to repair a broken user-level wrapper.
Locate a working executable or fix the user environment. Keep credentials
outside the repository.

## 5. Configure OpenCode when selected

Check:

```bash
opencode --version
opencode auth list
opencode models
```

Guide the user through `/connect` in the OpenCode TUI when login is required.
Ask which coding plan or API provider they intend to use, guide its connection
flow, and then let the user choose one of the models shown by `opencode
models`. Never request credential values or copy OpenCode's credential store
into Rethlas.

The bundled patch has no default provider, model, variant, or API key. With no
per-run override, OpenCode uses the user's own configuration. Optional
`OPENCODE_GENERATION_MODEL` and `OPENCODE_VERIFICATION_MODEL` values must come
from the user's selected `provider/model`.

## 6. Validate without a model call

Confirm:

- both Python environments use the intended interpreter;
- generation MCP dependencies import successfully;
- verification API dependencies import successfully;
- selected CLI executables resolve correctly;
- authentication status is known without revealing secrets;
- optional Poppler and Zola status matches the user's intended features.

Report each item as ready, missing, optional, or awaiting user action. Ask
before a provider login flow or paid model smoke test.

## Phase boundary

After validation, return to the main `SKILL.md`. If OpenCode was selected and
the patch is absent, continue to the patch phase. If original Codex was
selected, continue directly to usage guidance.
