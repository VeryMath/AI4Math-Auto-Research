# Discover Math Problems

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

`discover-math-problems` helps a coding agent turn fuzzy mathematical background into a concrete research-state packet.

## When To Use It

Use this skill when you have:

- scattered notes, definitions, examples, or failed proof attempts;
- an open-ended mathematical direction but no clear problem ranking;
- immature theorem ideas that need counterexample pressure before proof work;
- a need for a resumable record of conjectures, evidence, and uncertainty.

## What It Produces

The agent should produce ranked problem menus, conjecture lattices, evidence ledgers, counterexample pressure notes, proof obligations, work orders, and a `research_state_packet`.

## Skill Entry Points

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

## Installation

Copy this to your coding agent:

```text
Please install the `discover-math-problems` skill from https://github.com/VeryMath/AI4Math-Auto-Research.git (branch: codex/discover-math-problems-skill). Read `.agent.md`, install the declared Skill entrypoint, verify that `$discover-math-problems` is discoverable, and tell me whether I need to restart the agent.
```

If you already have this skill repository locally, replace the repository URL
with the local folder path. The coding agent should handle cloning, linking,
configuration, reload/restart checks, and verification.

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
