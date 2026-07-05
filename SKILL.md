---
name: ai4math-auto-research
description: Route AI4Math automated mathematical research tasks to normalized skill packages in this repository.
---

# AI4Math Auto Research

Use this repository as a routing layer for AI4Math automated research workflows.

Concrete skills belong under `skills/<skill-name>/`. Before running a concrete
workflow, open that package and follow its package-local `SKILL.md`, README,
scripts, and references.

## Packages

- `skills/agent-laboratory-workflow/`: deploy, configure, validate, and launch
  bounded Agent Laboratory auto-research runs.
- `skills/discover-math-problems/`: convert fuzzy mathematical background into
  ranked problems, conjecture lattices, proof obligations, and work orders.
- `skills/proof-blueprint-review/`: coordinate agent-mediated proof
  generation, verifier-style review, repair hints, and proof acceptance reports.

## Repository Boundary

- Keep root documentation concise and focused on routing.
- Add new skill packages under `skills/` using kebab-case names.
- Keep related public references in the root README.
- Keep generated outputs, private notes, and local staging material out of
  release content.
