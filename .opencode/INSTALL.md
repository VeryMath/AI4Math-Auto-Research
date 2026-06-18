# OpenCode Loading Notes

This repository is an agent-mediated mathematical problem discovery Skill. The
shared Skill layer is `SKILL.md`, and this file only explains how to load it
from OpenCode.

## Use

Open the repository in OpenCode and ask the agent to read:

```text
AGENTS.md
SKILL.md
```

For substantive discovery work, the agent should also load the relevant
protocol file under `references/`.

## Boundary

Do not duplicate workflow rules in `.opencode/`. Keep discovery, conjecture
generation, pressure testing, and handoff behavior in the shared Skill layer.
