<div align="center">

# AI4Math · Auto Research

Agentic workflows for mathematical problem discovery, research-loop
orchestration, and proof-blueprint review.

[中文说明](README.zh-CN.md) · [Contributors](CONTRIBUTORS.md) · [Skill packages](#skill-packages) · [Installation](#installation) · [Quick start](#quick-start) · [References](#related-public-references) · [Security model](#security-and-scope)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-3-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

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
```

If your agent uses a different local Skill directory, replace `~/.codex/skills` with that configured path.

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

## Repository Layout

```text
AI4Math-Auto-Research/
├── README.md
├── README.zh-CN.md
├── SKILL.md
└── skills/
    ├── agent-laboratory-workflow/
    ├── discover-math-problems/
    └── proof-blueprint-review/
```

Keep package-owned examples, prompts, scripts, references, and benchmark notes
inside the package that owns them.

## Validation

There is no root build step. When changing a package, validate its `SKILL.md`,
README links, scripts, and package-local references. If you use Codex's local
skill validator, run it against every changed package directory.

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
