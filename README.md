# AI4Math Auto-Research

This repository contains the AI4Math Auto-Research Codex skill for deploying, testing, and using Agent Laboratory with a Codex-native fallback workflow.

## Skill

- `skills/AI4Math-Auto-Research/agent-laboratory-workflow`

The skill supports:

- `hybrid`: recommended. Try bounded Agent Laboratory first, then hand unfinished phases to Codex.
- `codex-native`: no extra model API. Create a Codex research workspace and let the coding agent finish literature review, plan, experiment, interpretation, and report directly.
- `core`, `research`, and `full`: Agent Laboratory validation and upstream workflow modes.

## Quick Start

```bash
python skills/AI4Math-Auto-Research/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --wizard \
  --wizard-mode hybrid \
  --research-topic "USER_RESEARCH_TOPIC" \
  --env-manager conda \
  --llm-model-id ecnu-plus \
  --lightweight-imports \
  --yes
```

Codex-native mode avoids an extra LLM API key:

```bash
python skills/AI4Math-Auto-Research/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --wizard \
  --wizard-mode codex-native \
  --research-topic "USER_RESEARCH_TOPIC" \
  --codex-workspace-dir codex_research \
  --yes
```

## Development

Install the lightweight test dependency, then run the tests:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -v
```

Do not commit local deployments, generated research workspaces, runtime YAMLs, or API keys.
