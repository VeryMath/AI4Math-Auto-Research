# Codex Loading Notes

This repository is an agent-mediated mathematical problem discovery Skill.
Codex can use it directly from the checkout or by linking this directory into a
local Skill path. The shared Skill layer is `SKILL.md`.

## Use From Checkout

Ask Codex to read:

```text
AGENTS.md
SKILL.md
```

Then provide background notes, a mathematical domain, failed proof attempts,
candidate ideas, or source artifacts.

## Local Skill Link

If local Skill discovery is desired, link this directory:

```bash
ln -s "$PWD/skills/discover-math-problems" ~/.codex/skills/discover-math-problems
```

Reload Codex if needed, then invoke:

```text
Use $discover-math-problems.
```

Keep `.codex/` as a thin adapter. Workflow changes belong in `SKILL.md` or
`references/`.
