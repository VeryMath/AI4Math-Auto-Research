# Rethlas OpenCode Adapter

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

`rethlas-opencode-adapter` helps a coding agent clone FrenzyMath Rethlas, apply an OpenCode adapter patch, and run the standard Rethlas generation/verification workflow through a user's existing OpenCode installation.

## When To Use It

Use this skill when:

- the user wants to deploy Rethlas on a machine with OpenCode already installed;
- the user wants to run Rethlas proof generation without setting up Codex CLI;
- the user wants a coding agent to patch a fresh Rethlas clone and then supervise the standard `tests/run_example.sh` workflow.

## What It Produces

The adapter produces a patched Rethlas clone with:

- an OpenCode-capable generation runner;
- an OpenCode-capable verification service;
- generation-side `.opencode` agent and MCP configuration;
- verification-side `.opencode` agent and MCP configuration.

It does not add example problems, generated proofs, test caches, or user credentials.

## Skill Entry Points

Load this package directory when using it directly:

```text
skills/rethlas-opencode-adapter/
```

Core files:

- `SKILL.md`: main operating contract for the coding agent.
- `scripts/apply_adapter.py`: clone-or-patch helper for Rethlas.

## Installation

Copy this to your coding agent:

```text
Please install the `rethlas-opencode-adapter` skill from https://github.com/VeryMath/AI4Math-Auto-Research.git. Read the package `SKILL.md`, install the declared Skill entrypoint, verify that `$rethlas-opencode-adapter` is discoverable, and tell me whether I need to restart the agent.
```

If you already have this skill repository locally, replace the repository URL with the local folder path.

## Quick Start

```text
Use $rethlas-opencode-adapter.

Clone FrenzyMath Rethlas into ./external/Rethlas, apply the OpenCode adapter,
prepare my problem file under agents/generation/data/, install dependencies in
Python virtual environments, start the verification service with OpenCode, run
the generation runner with OpenCode, and supervise only the outer process until
blueprint_verified.md appears.
```

## Maintainer Checks

Validate the Skill shape after edits:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/rethlas-opencode-adapter
```

Run the adapter script's static checks:

```bash
python3 -B skills/rethlas-opencode-adapter/scripts/apply_adapter.py --help >/dev/null
python3 - <<'PY'
from pathlib import Path
import ast
ast.parse(Path("skills/rethlas-opencode-adapter/scripts/apply_adapter.py").read_text())
PY
```

