---
name: rethlas-opencode-adapter
description: "Use when a coding agent should clone, patch, set up, and supervise FrenzyMath Rethlas on a machine that already has OpenCode installed and configured."
---

# Rethlas OpenCode Adapter

Use this skill when the user wants to deploy FrenzyMath Rethlas on a machine that already has OpenCode installed and configured.

Trigger this skill for requests such as:

- Deploy Rethlas with OpenCode.
- Adapt Rethlas for a user who has OpenCode installed.
- Run Rethlas without Codex CLI.
- Set up Rethlas proof generation and verification through OpenCode.

The target workflow is:

1. Clone Rethlas.
2. Apply the OpenCode adapter patch.
3. Put a problem markdown file under `agents/generation/data/`.
4. Start the verification service with OpenCode.
5. Run `agents/generation/tests/run_example.sh` with OpenCode.
6. Let Rethlas produce `agents/generation/results/<problem_id>/blueprint_verified.md`.

Do not edit the user's global OpenCode configuration unless the user explicitly asks for provider/model setup.

Do not add test problems, unit tests, README edits, or generated caches as part of the adapter patch.

## Security and scope

- Run the adapter only against a dedicated Rethlas clone.
- Review `git diff` after patching and before launching OpenCode with `--auto`.
- Keep API keys, provider credentials, private notes, and unpublished research data out of problem files and references unless the user explicitly approves that scope.
- Do not run dependency installation or agent execution as root.
- Do not pass API keys through command-line arguments.
- Keep `OPENCODE_MODEL` unset when the user wants to use their existing OpenCode provider/model configuration.
- Stop and ask before patching a clone with unrelated local edits.

## Locate this skill

Set `SKILL_DIR` to the directory that contains this `SKILL.md`, then use:

```bash
ADAPTER_SCRIPT="$SKILL_DIR/scripts/apply_adapter.py"
```

When working inside Codex, resolve `SKILL_DIR` from the expanded skill path. When working from a copied skill directory, use that copied directory.

## Preflight checks

Check the local tools before patching:

```bash
git --version
python3 --version
opencode --version
```

If `opencode --version` fails, stop and ask the user to install or configure OpenCode first.

If `python3 -m venv --help` fails, stop and report that a Python venv-capable installation is required.

## Files added or changed by the adapter

The adapter script changes only these paths inside the Rethlas clone:

```text
agents/generation/tests/run_example.sh
agents/verification/api/server.py
agents/generation/.opencode/.gitignore
agents/generation/.opencode/AGENTS.md
agents/generation/.opencode/agent/rethlas-generation.md
agents/generation/.opencode/agent/rethlas-generation-no-search.md
agents/generation/.opencode/agent/subgoal-prover.md
agents/generation/.opencode/opencode.json
agents/verification/.opencode/.gitignore
agents/verification/.opencode/AGENTS.md
agents/verification/.opencode/agent/rethlas-verification.md
agents/verification/.opencode/opencode.json
```

## Apply the adapter

From any working directory:

```bash
python3 "$ADAPTER_SCRIPT" \
  --target /path/to/Rethlas \
  --clone
```

If the Rethlas clone already exists:

```bash
python3 "$ADAPTER_SCRIPT" \
  --target /path/to/Rethlas
```

For an existing clone with local edits, stop and ask the user before using `--allow-dirty`.

After patching, run these static checks from the Rethlas clone:

```bash
bash -n agents/generation/tests/run_example.sh
python3 -m py_compile agents/verification/api/server.py
python3 -m json.tool agents/generation/.opencode/opencode.json >/dev/null
python3 -m json.tool agents/verification/.opencode/opencode.json >/dev/null
```

## Prepare a problem file

Write the user's problem under `agents/generation/data/`. For display math in markdown files, use `$$`.

Example:

```bash
mkdir -p /path/to/Rethlas/agents/generation/data/user
$EDITOR /path/to/Rethlas/agents/generation/data/user/problem.md
```

The `problem_id` becomes the path under `data/` without `.md`. For the example above, it is `user/problem`.

## Install dependencies

Verification side:

```bash
cd /path/to/Rethlas/agents/verification
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Generation side:

```bash
cd /path/to/Rethlas/agents/generation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r mcp/requirements.txt
```

If the user asks to use `uv`, the equivalent commands are `uv venv` and `uv pip install ...`.

## Run Rethlas with OpenCode

Terminal 1:

```bash
cd /path/to/Rethlas/agents/verification
source .venv/bin/activate
VERIFY_EXECUTOR=opencode python -m uvicorn api.server:app --host 127.0.0.1 --port 8091
```

Terminal 2:

```bash
cd /path/to/Rethlas/agents/generation
source .venv/bin/activate
EXECUTOR=opencode PROBLEM_FILE=data/user/problem.md ./tests/run_example.sh
```

Leave `OPENCODE_MODEL` unset when the user wants to use the model already configured in OpenCode.

To override the model for this run:

```bash
EXECUTOR=opencode OPENCODE_MODEL=provider/model PROBLEM_FILE=data/user/problem.md ./tests/run_example.sh
```

## Supervision rules

During a run, supervise the outer process only:

- Watch the verification service health and HTTP status lines.
- Watch the runner stdout and exit code.
- Check whether `blueprint_verified.md` exists.
- Avoid editing memory files, blueprint files, iteration logs, prompts, or agent outputs mid-run.

The success artifact is:

```text
/path/to/Rethlas/agents/generation/results/<problem_id>/blueprint_verified.md
```

If the runner exits without that file, report the exit code and the paths to the runner log directory and verification logs.
