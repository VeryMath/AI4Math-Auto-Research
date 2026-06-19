# Claude Code Adapter

This repository is an agent-mediated mathematical problem discovery Skill.
The shared Skill layer is `SKILL.md`; Claude-specific behavior should stay in
this thin adapter instead of forking the workflow.

Skill layer: `SKILL.md`.

## Use

1. Read `AGENTS.md` for the repository contract.
2. Read `SKILL.md` for the core problem-discovery loop.
3. Load files under `references/` only when the current task needs detailed
   artifact, conjecture-generation, or autonomous-research protocol.

## Boundary

Do not run theorem proving from this adapter. Handoff proof-ready obligations to
`rethlas-proving`.
