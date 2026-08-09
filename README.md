<div align="center">

# AI4Math · Auto Research

Agentic workflows for mathematical problem discovery, research-loop
orchestration, and proof-blueprint review.

[中文说明](README.zh-CN.md) · [Contributors](CONTRIBUTORS.md) · [Skill packages](#skill-packages) · [Installation](#installation) · [Quick start](#quick-start) · [References](#related-public-references) · [Security model](#security-and-scope)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-8-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

<p align="center">
  If this project helps your work, please consider giving the repository a Star ⭐
  <a href="https://github.com/VeryMath/AI4Math-Auto-Research"><img alt="GitHub stars" src="https://img.shields.io/github/stars/VeryMath/AI4Math-Auto-Research?style=social"></a>
</p>

## What This Repository Is

This repository is the AI4Math home for auto-research skills. It collects
focused Skill-as-adapter packages for turning broad mathematical intent into
structured problems, bounded research runs, and reviewed proof plans.

Use this page as the public map. For real work, open the package that matches
the task and follow its package-local instructions.

## Skill Packages

| Package | Use it for | Start here |
| --- | --- | --- |
| [`agent-laboratory-workflow`](skills/agent-laboratory-workflow/) | Deploy, validate, and launch bounded Agent Laboratory auto-research runs. | [`README`](skills/agent-laboratory-workflow/README.md) · [`SKILL`](skills/agent-laboratory-workflow/SKILL.md) |
| [`discover-math-problems`](skills/discover-math-problems/) | Convert fuzzy background into ranked problems, conjecture lattices, evidence ledgers, and work orders. | [`README`](skills/discover-math-problems/README.md) · [`SKILL`](skills/discover-math-problems/SKILL.md) |
| [`proof-blueprint-review`](skills/proof-blueprint-review/) | Build proof blueprints, run verifier-style reviews, record repair hints, and issue strict proof-status reports. | [`README`](skills/proof-blueprint-review/README.md) · [`SKILL`](skills/proof-blueprint-review/SKILL.md) |
| [`rethlas-helper`](skills/rethlas-helper/) | Install Rethlas for OpenCode, remember its local path, and run natural-language proof generation from any OpenCode project. | [`SKILL`](skills/rethlas-helper/SKILL.md) |
| [`archon-helper`](skills/archon-helper/) | Install Archon for OpenCode, remember its local path, and run formalization workflows from any OpenCode project. | [`SKILL`](skills/archon-helper/SKILL.md) |
| [`graph-theory-researcher`](skills/graph-theory-researcher/) | Read graph-theory papers, select questions through user gates, run bounded research, and prepare verified LaTeX/PDF artifacts. | [`README`](skills/graph-theory-researcher/README.md) · [`SKILL`](skills/graph-theory-researcher/SKILL.md) |
| [`extremal-graph-problem-suggester`](skills/extremal-graph-problem-suggester/) | Generate small-move candidate variants for extremal graph problems with citation, novelty, and feasibility checks. | [`README`](skills/extremal-graph-problem-suggester/README.md) · [`SKILL`](skills/extremal-graph-problem-suggester/SKILL.md) |
| [`open-problem-research-pipeline`](skills/open-problem-research-pipeline/) | Run a staged literature-search, method-analysis, proof-framework, and report workflow for open mathematical problems. | [`README`](skills/open-problem-research-pipeline/README.md) · [`SKILL`](skills/open-problem-research-pipeline/SKILL.md) |

## Installation

The recommended path is AI-assisted installation: ask your coding agent to clone or update this repository, read the Skill instructions, install the entrypoints, and verify discovery.

```text
Please install these AI4Math Skills for me.

Repository: https://github.com/VeryMath/AI4Math-Auto-Research.git
Branch: main
Skill paths:
- skills/agent-laboratory-workflow
- skills/discover-math-problems
- skills/proof-blueprint-review
- skills/rethlas-helper
- skills/archon-helper
- skills/graph-theory-researcher
- skills/extremal-graph-problem-suggester
- skills/open-problem-research-pipeline

Steps:
1. Clone or update the repository locally.
2. Read README.md, SKILL.md, AGENTS.md if present, and each target Skill entrypoint.
3. If this environment supports local Skill discovery, link each directory that contains SKILL.md into the local skills directory.
4. Keep shared sibling support directories in place when a Skill depends on them.
5. Verify that the installed Skills are discoverable.
6. Tell me the installed paths, whether a restart is needed, and give me one test prompt.
```

Manual fallback for Codex-style local discovery:

```bash
git clone https://github.com/VeryMath/AI4Math-Auto-Research.git
cd AI4Math-Auto-Research
mkdir -p ~/.codex/skills
ln -s "$PWD/skills/agent-laboratory-workflow" ~/.codex/skills/agent-laboratory-workflow
ln -s "$PWD/skills/discover-math-problems" ~/.codex/skills/discover-math-problems
ln -s "$PWD/skills/proof-blueprint-review" ~/.codex/skills/proof-blueprint-review
ln -s "$PWD/skills/rethlas-helper" ~/.codex/skills/rethlas-helper
ln -s "$PWD/skills/archon-helper" ~/.codex/skills/archon-helper
ln -s "$PWD/skills/graph-theory-researcher" ~/.codex/skills/graph-theory-researcher
ln -s "$PWD/skills/extremal-graph-problem-suggester" ~/.codex/skills/extremal-graph-problem-suggester
ln -s "$PWD/skills/open-problem-research-pipeline" ~/.codex/skills/open-problem-research-pipeline
```

If your agent uses a different local Skill directory, replace `~/.codex/skills` with that configured path.

OpenCode Desktop discovers global Skills from `~/.config/opencode/skills`.
Install the Rethlas and Archon helpers globally with:

```bash
mkdir -p ~/.config/opencode/skills
ln -s "$PWD/skills/rethlas-helper" ~/.config/opencode/skills/rethlas-helper
ln -s "$PWD/skills/archon-helper" ~/.config/opencode/skills/archon-helper
```

## Quick Start

Clone the repository and choose a package:

```bash
git clone https://github.com/VeryMath/AI4Math-Auto-Research.git
cd AI4Math-Auto-Research
```

For problem discovery, start with:

```text
skills/discover-math-problems/SKILL.md
```

For proof-plan review, start with:

```text
skills/proof-blueprint-review/SKILL.md
```

For Agent Laboratory runs, start with:

```text
skills/agent-laboratory-workflow/SKILL.md
```

For a persistent Rethlas installation available from OpenCode projects and
conversations, start with:

```text
skills/rethlas-helper/SKILL.md
```

For a persistent Archon installation available from OpenCode projects and
conversations, start with:

```text
skills/archon-helper/SKILL.md
```

For the course-contributed graph-theory and open-problem workflows, start with:

```text
skills/graph-theory-researcher/SKILL.md
skills/extremal-graph-problem-suggester/SKILL.md
skills/open-problem-research-pipeline/SKILL.md
```

## Repository Layout

```text
AI4Math-Auto-Research/
├── README.md
├── README.zh-CN.md
├── SKILL.md
└── skills/
    ├── agent-laboratory-workflow/
    ├── discover-math-problems/
    ├── proof-blueprint-review/
    ├── rethlas-helper/
    ├── archon-helper/
    ├── graph-theory-researcher/
    ├── extremal-graph-problem-suggester/
    └── open-problem-research-pipeline/
```

Keep package-owned examples, prompts, scripts, references, and benchmark notes
inside the package that owns them.

## Validation

Run:

```bash
python3 -m unittest discover -s tests -v
bash skills/graph-theory-researcher/scripts/validate-skill.sh
```

If you use Codex's local skill validator, run it against every changed package
directory.

## Related Public References

Related public reference materials:

- [Agent Laboratory](https://github.com/SamuelSchmidgall/AgentLaboratory)
- [Rethlas](https://github.com/frenzymath/Rethlas)
- [Automated Conjecture Resolution with Formal Verification](https://arxiv.org/abs/2604.03789)
- [Archon](https://github.com/frenzymath/Archon)
- [LeanSearch](https://github.com/frenzymath/LeanSearch)

## Security and Scope

Do not commit API keys, model credentials, private research notes, generated
auto-research outputs, `.env` files, or local staging material. Public examples
should be small, source-attributed, and safe to redistribute.
