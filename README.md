# Discover Math Problems

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

`discover-math-problems` is an AI4Math Skill-as-adapter package for mathematical
problem discovery and conjecture generation. It helps a coding agent turn fuzzy
background, scattered notes, failed proof attempts, and immature theorem ideas
into a ranked problem menu, conjecture lattice, evidence ledger, counterexample
pressure, proof obligations, and a resumable research-state packet.

Use this when a user wants a standalone research-state builder for
mathematical problem discovery. No other AI4Math skill is required to start.

## What This Skill Does

This standalone skill helps a coding agent:

- turn fuzzy mathematical background into explicit objects, assumptions, and examples;
- rank candidate problems instead of committing to the first plausible theorem;
- build conjecture lattices and pressure-test them with toy models and counterexamples;
- record evidence, uncertainty, proof obligations, and a resumable research-state packet.

Use it directly when you have notes, definitions, failed attempts, or an open-ended
research direction and want the agent to organize the next mathematical questions.

## What You Install Or Load

Load the repository root when using this as a standalone package:

```text
discover-math-problems/
```

Core files:

- `SKILL.md`: shared Skill layer and main entrypoint.
- `AGENTS.md`: coding-agent contract.
- `references/autonomous-research-protocol.md`: end-to-end discovery loop.
- `references/conjecture-generation-protocol.md`: conjecture lattice and stress testing.
- `references/artifact-contract.md`: artifact names, fields, and status labels.

## Installation / Loading

Clone or open this skill repository in your coding-agent environment. Then ask
the coding agent to read:

```text
AGENTS.md
SKILL.md
```

If the target agent supports local Skill discovery, install or link this folder
into that agent's Skill path and reload the agent if needed.

Codex example:

```bash
ln -s "$PWD" ~/.codex/skills/discover-math-problems
```

Platform notes live in `CLAUDE.md`, `GEMINI.md`, `.codex/INSTALL.md`, and
`.opencode/INSTALL.md`.

## Quick Start

```text
Use $discover-math-problems.

I have background notes and a few immature theorem ideas. Build a research state,
rank candidate problems, generate a conjecture lattice, pressure-test the
strongest candidates, and produce proof obligations for later review.
```

Useful inputs include domain background, source notes, definitions, examples,
failed proof attempts, open-ended research goals, and partially formed
conjectures.

## How To Interact

Use a checkpoint loop:

```text
background or immature idea
  -> background map
  -> problem menu
  -> conjecture lattice
  -> evidence ledger and counterexample pressure
  -> proof obligations
  -> approve / revise / reject / skip
  -> next discovery pass or final research-state packet
```

Use `approve` to run the proposed next discovery step, `revise` to adjust the
domain, assumptions, source scope, or candidate ranking, `reject` to stop the
current direction, and `skip` to move past a nonessential phase. The agent
should ask before changing the central mathematical object, accepting a strong
external theorem as a black box, discarding a user-preferred direction, spending
a long run on source acquisition or computational search, or promoting a
candidate to `verification_ready`.

## Artifact Contract

Substantive discovery work should create or update:

- `background_map.md` and `background_map.json`
- `problem_menu.md` and `problem_menu.json`
- `conjecture_lattice.md` and `conjecture_lattice.json`
- `evidence_ledger.json`
- `counterexample_pressure.md`
- `proof_obligations.md` and `proof_obligations.json`
- `work_orders.md` and `work_orders.json`
- `research_state_packet.json`
- `human_decision_brief.md`

Status labels should stay honest: `background_map`, `candidate_problem_menu`,
`candidate_conjecture`, `stress_tested_conjecture`, `proof_obligations_ready`,
or `verification_ready`. `verification_ready` means ready for verification work,
not already verified. Never call a conjecture a theorem.

## Maintainer Checks

Validate the Skill shape after edits:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/discover-math-problems
```

Repository-level adapter checks live in the parent AI4Math Skill Library.
