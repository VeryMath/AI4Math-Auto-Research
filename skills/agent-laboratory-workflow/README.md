# Agent Laboratory Workflow

`agent-laboratory-workflow` helps a coding agent deploy, configure, validate,
and launch bounded AI4Math Auto-Research runs through Agent Laboratory.

## Entry Point

Start with [`SKILL.md`](SKILL.md). It defines the deployment gates, API-key
handling, research-topic intake, smoke checks, and recovery flow for incomplete
Agent Laboratory runs.

## Package Layout

- `agents/`: agent-facing metadata.
- `references/`: deployment and operational guidance.
- `scripts/`: helper commands for bootstrap, run inspection, and Codex research
  workspace handoff.
- `templates/`: experiment YAML templates for interactive auto-research runs.

## Validation

Run from the repository root:

```bash
python3 -m unittest discover -s tests -v
```
