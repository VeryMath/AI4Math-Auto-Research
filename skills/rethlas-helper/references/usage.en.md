# Solve Natural-Language Mathematics Problems with Rethlas

Rethlas reads a Markdown mathematics problem, generates an informal proof
blueprint, and asks a separate verification agent to inspect logic, references,
and proof gaps. The generation agent revises the proof across multiple rounds
using the verification report.

## 1. Locate Rethlas from any conversation

Run before each task:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor --json
```

Set `TARGET` to the reported `repository`. A valid remembered installation can
proceed directly to problem setup. When OpenCode requests external-directory
access from a new project, show the path to the user and request access.

## 2. Prepare the problem

Store the problem at:

```text
$TARGET/agents/generation/data/<problem_id>.md
```

When the user provides a problem directly in conversation, choose a clear
`problem_id` and write the complete statement to the Markdown file. Example:

```markdown
# Problem

Prove that every finite tree with at least two vertices has at least two leaves.
```

Place problem-specific references in:

```text
data/<problem_id>.refs/
```

References may be Markdown, TeX, plain text, or PDF. PDF extraction uses
`pdftotext`.

## 3. Start the OpenCode verification service

From an OpenCode Desktop workspace terminal:

```bash
cd "$TARGET/agents/verification"
source .venv/bin/activate
uvicorn api.server_opencode:app --host 127.0.0.1 --port 8091
```

With a user-selected verification model:

```bash
OPENCODE_VERIFICATION_MODEL="provider/model" \
  uvicorn api.server_opencode:app --host 127.0.0.1 --port 8091
```

Confirm a healthy response from `http://127.0.0.1:8091/health`, then keep that
terminal session running.

## 4. Run proof generation

From another workspace terminal:

```bash
cd "$TARGET/agents/generation"
source .venv/bin/activate
PROBLEM_FILE="data/<problem_id>.md" ./tests/run_example_opencode.sh
```

With a selected generation model or iteration bound:

```bash
OPENCODE_GENERATION_MODEL="provider/model" \
MAX_ITERATIONS=10 \
PROBLEM_FILE="data/<problem_id>.md" \
  ./tests/run_example_opencode.sh
```

The runner keeps one OpenCode session during the run, alternates independent
reasoning and retrieval, and repairs the proof from verification reports.
State the provider/model and quota use before the real model call.

## 5. Read progress and results

For a relative `<problem_id>`, inspect:

```text
$TARGET/agents/generation/memory/opencode/<problem_id>/
$TARGET/agents/generation/logs/opencode/<problem_id>/iter/
$TARGET/agents/generation/results/opencode/<problem_id>/blueprint.md
$TARGET/agents/generation/results/opencode/<problem_id>/blueprint_verified.md
```

`blueprint.md` is the current proof blueprint. Successful verification produces
`blueprint_verified.md`. Report the problem path, model, iteration count,
verdict, result path, and log path.

With Zola installed, serve the local result site from the generation directory:

```bash
./site/serve.sh
```

Open `http://localhost:3264`.

## 6. OpenCode Desktop conversation example

The user can start a new conversation in any project and say:

> Use Rethlas to prove that every finite tree with at least two vertices has at
> least two leaves. Keep reporting generation, verification, and repair
> progress, then give me the final proof blueprint and file paths.

Load the remembered `rethlas_home`, create the problem file, start verification
and generation, and follow the run from the current conversation.

## 7. Common checks

- moved or invalid remembered installation;
- pending `external_directory` access in a new project;
- port 8091 already in use;
- OpenCode provider connection;
- `PROBLEM_FILE` path;
- generation and verification MCP state;
- remaining gaps after the iteration bound.
