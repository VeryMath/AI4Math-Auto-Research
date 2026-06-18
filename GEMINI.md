# Gemini Adapter

This repository is an agent-mediated mathematical problem discovery Skill. The
shared Skill layer is `SKILL.md`; Gemini-specific notes should remain a thin
loading adapter.

Skill layer: `SKILL.md`.

## Use

1. Read `AGENTS.md`.
2. Read `SKILL.md`.
3. Load the relevant `references/` protocol file when the task reaches
   conjecture generation, artifact production, pressure testing, or handoff.

## Boundary

Do not fork the discovery workflow in this file. Improve the shared Skill layer
or its reference contracts when behavior changes.
