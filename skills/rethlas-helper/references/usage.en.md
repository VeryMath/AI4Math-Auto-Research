# Rethlas Features and Usage

Use this reference to explain what Rethlas does and guide a first useful run.
Adapt commands to the runtime the user selected.

## Contents

1. Feature map
2. Start verification
3. Run proof generation
4. Add a custom problem
5. Supply private references
6. Read outputs and logs
7. Browse the result website
8. Guide and troubleshoot

## 1. Feature map

Rethlas is a natural-language mathematical reasoning system with two main
agents:

- **Generation agent:** reads a Markdown problem and writes an informal proof
  blueprint.
- **Verification agent:** checks a blueprint and returns a structured verdict
  through a local HTTP API.

The generation runner maintains one model session across iterations. It
alternates retrieval-disabled and retrieval-enabled turns, uses verifier
feedback to repair the proof, and stops when a verified blueprint appears or
the iteration limit is reached.

Supporting features:

- problem-specific Markdown, TeX, text, or PDF references;
- reusable memory artifacts;
- per-iteration logs;
- separate draft and verified results;
- a Zola website for browsing Markdown results with LaTeX math;
- optional additive OpenCode runtime alongside the original Codex runtime.

Explain only the features relevant to the user's goal, then give the next
concrete command.

## 2. Start verification

Start this service before generation. From `agents/verification`, activate its
environment.

Original Codex-backed verifier:

```bash
source .venv/bin/activate
uvicorn api.server:app --host 127.0.0.1 --port 8091
```

OpenCode-backed verifier, available only after patch installation:

```bash
source .venv/bin/activate
uvicorn api.server_opencode:app --host 127.0.0.1 --port 8091
```

Both use port 8091; run only the verifier matching the selected generation
runtime. Keep this terminal open and report startup errors before proceeding.

## 3. Run proof generation

In another terminal, enter `agents/generation` and activate its environment.

Original Codex workflow:

```bash
source .venv/bin/activate
./tests/run_example.sh
```

OpenCode workflow:

```bash
source .venv/bin/activate
./tests/run_example_opencode.sh
```

Before an OpenCode run, confirm the user's own provider/API connection and
model selection:

```bash
opencode auth list
opencode models
```

The patch supplies no default model. Leaving the model environment variables
unset uses the user's OpenCode configuration. To pin both processes, use the
user-selected model id:

```bash
OPENCODE_GENERATION_MODEL="provider/model" \
  ./tests/run_example_opencode.sh
```

```bash
OPENCODE_VERIFICATION_MODEL="provider/model" \
  uvicorn api.server_opencode:app --host 127.0.0.1 --port 8091
```

Bound the repair loop when desired:

```bash
MAX_ITERATIONS=10 ./tests/run_example.sh
```

Use the corresponding OpenCode script for an OpenCode run. Ask before the
first model-backed run and state which provider/model will be charged or
consume plan quota.

## 4. Add a custom problem

Store the problem as Markdown under `agents/generation/data/`, for example:

```text
agents/generation/data/my_problem.md
```

Run Codex:

```bash
PROBLEM_FILE=data/my_problem.md ./tests/run_example.sh
```

Run OpenCode:

```bash
PROBLEM_FILE=data/my_problem.md ./tests/run_example_opencode.sh
```

Subdirectories are supported:

```bash
PROBLEM_FILE=data/modrep/modrep.md ./tests/run_example.sh
```

Generated artifacts preserve the problem's relative directory structure.

## 5. Supply private references

Create a sibling directory with the problem's stem:

```text
data/modrep/modrep.md
data/modrep/modrep.refs/
```

The generation agent reads these references before external retrieval. Prefer
Markdown, TeX, or plain text. PDF support requires `pdftotext`; extracted PDF
text is written below `.extracted/`.

Do not add unpublished or sensitive references to Git unless the user
explicitly intends to version them.

## 6. Read outputs and logs

For the original example, inspect:

```text
memory/example/
logs/example/iter/
results/example/blueprint.md
results/example/blueprint_verified.md
```

`blueprint.md` is the current draft. `blueprint_verified.md` appears after
successful verification. If no verified file appears, inspect the iteration
logs and verifier terminal before concluding that the system failed.

OpenCode isolates example artifacts below:

```text
memory/opencode/example/
logs/opencode/example/
results/opencode/example/
```

This keeps Codex and OpenCode runs from overwriting one another.

## 7. Browse the result website

With Zola installed, run from `agents/generation`:

```bash
./site/serve.sh
```

The first run downloads the MATbook theme and requires network access. The
site serves locally at `http://localhost:3264` and organizes results using the
problem directory structure.

## 8. Guide and troubleshoot

For guided use:

1. State the feature and expected outcome.
2. Confirm the working directory and active `.venv`.
3. Start the matching verifier and confirm port 8091 is listening.
4. Show or run one generation command.
5. Point to the exact result and log paths.
6. Interpret failures and propose the smallest next check.

Common checks:

- port 8091 conflict or wrong verifier runtime;
- missing provider login;
- wrong `PROBLEM_FILE` path;
- missing PDF extractor;
- generation and verification MCP connection status;
- iteration limit reached before verification;
- no user-selected OpenCode provider or model;
- model or variant unavailable for the selected provider.

Report the runtime, model, problem path, result path, log path, and final
verification state.
