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
- `skills/rethlas-helper/`: install and configure Rethlas, choose the original
  Codex runtime or the additive OpenCode runtime, and guide proof-generation
  and verification workflows.
- `skills/archon-helper/`: install and configure Archon, choose Claude Code or
  OpenCode, apply the compatibility patch when selected, and guide
  formalization workflows.
- `skills/graph-theory-researcher/`: stage graph-theory reading, question
  selection, bounded research, verification, and LaTeX/PDF delivery.
- `skills/extremal-graph-problem-suggester/`: generate small-move candidate
  variants for extremal graph problems with evidence-status checks.
- `skills/open-problem-research-pipeline/`: route a literature-search,
  method-analysis, candidate proof-framework, and report workflow.

## Repository Boundary

- Keep root documentation concise and focused on routing.
- Add new skill packages under `skills/` using kebab-case names.
- Keep related public references in the root README.
- Keep generated outputs, private notes, and local staging material out of
  release content.
