# AI4Math Auto Research

AI4Math Auto Research collects Skill-as-adapter packages for automated
mathematical research workflows, including problem discovery, hypothesis
generation, experiment planning, and research-loop orchestration.

## Skill Packages

Skill packages live under `skills/<skill-name>/`.

| Package | Purpose | Status |
| --- | --- | --- |
| `skills/agent-laboratory-workflow/` | Agent Laboratory deployment, validation, and bounded auto-research runs. | `README.md`, `SKILL.md` |
| `skills/discover-math-problems/` | Turn fuzzy mathematical background into problem menus, conjectures, and work orders. | `README.md`, `SKILL.md` |
| `skills/agentic-rethlas-proving/` | Rethlas/Rethlab-style proof blueprint, verification, and repair workflow. | `README.md`, `SKILL.md` |

## Usage

Use this repository as the public home for AI4Math auto-research skills. New
packages should be added under `skills/<skill-name>/` with their own `README.md`
and `SKILL.md` files.

Keep root files focused on routing and repository-level guidance. Put long
examples, prompts, scripts, references, and benchmark notes inside the package
that owns them.
