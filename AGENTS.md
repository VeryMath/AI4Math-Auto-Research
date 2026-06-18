# AGENTS.md

## Project Goal

This repository exposes an agent-mediated mathematical problem discovery and
conjecture-generation Skill for AI4Math research. The shared Skill layer is
`SKILL.md`, with detailed artifact and autonomous research contracts under
`references/`.

The goal is to turn fuzzy mathematical background, notes, failed proof attempts,
and immature ideas into ranked candidate problems, conjecture lattices, evidence
ledgers, counterexample pressure, proof obligations, and resumable research
state packets.

## Source of Truth

Read `SKILL.md` first. Load reference files only when the active research task
needs them:

- `references/autonomous-research-protocol.md`
- `references/conjecture-generation-protocol.md`
- `references/artifact-contract.md`

## Operating Rules

- Keep platform-specific files thin and point back to the shared Skill layer.
- Never call a conjecture a theorem.
- Never call a proof sketch verified.
- Keep external proof tools outside this skill's status ladder.
- Preserve source uncertainty, novelty uncertainty, and counterexample pressure.
- Produce explicit proof obligations before handing work to theorem proving.

## Done Means

A substantive discovery task is done only when the agent has created or updated
the requested research-state artifacts, ranked candidate directions, recorded
evidence and pressure, and labeled the handoff status honestly.
