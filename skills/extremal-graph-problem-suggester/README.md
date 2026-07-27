# Extremal Graph Problem Suggester

A coding-agent Skill that generates candidate research variants for Turán-type
extremal graph theory problems of the form "forbid subgraph X, maximize
parameter Y".

## Overview

Given a user's extremal graph theory problem, this skill produces **1 primary recommendation + 1 backup**, each modifying either the forbidden subgraph or the maximized parameter to produce a promising new research direction.

## Design Principle: Small Moves

The skill intentionally avoids hard open problems, hypergraph generalizations, or technically heavy methods (flag algebra, regularity, absorption). Instead it focuses on **small, tractable modifications**:

- Change a parameter: `C_k → C_{k+1}`, `K_r → K_{r+1}`, `P_k → P_{k+1}`
- Restrict to bipartite graphs
- Change edge count to triangle count (generalized Turán)
- Change edge count to spectral radius
- Switch from single forbidden graph to double forbidden
- Change graph class (general → planar, etc.)

## Output Format

Each recommendation includes:
1. **Problem statement**: forbid X, maximize Y
2. **Rationale**: 2–4 sentences + 1–2 references (author, year, key result)
3. **Method sketch**: 2–3 sentences outlining the technical approach

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Main skill definition with instructions and frontmatter |
| `evals/evals.json` | 3 evaluation test cases (Turán, C₄, P₋ problems) |

## Requirements

- No Python package dependency.
- Literature verification requires a browser or paper database appropriate to
  the user's environment.

## Testing

The skill comes with three evaluation prompts in `evals/evals.json`. They are
behavioral scenarios, not proof that a suggested problem is new or tractable.

## Contributor and License

Course contributor: **Miao Dong**. Released under the repository's MIT
License. See [`PROVENANCE.yaml`](PROVENANCE.yaml) and
[`NORMALIZATION.md`](NORMALIZATION.md).
