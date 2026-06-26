<div align="center">

# AI4Math · Auto Research

Agentic workflows for mathematical problem discovery, research-loop
orchestration, and proof-blueprint review.

[中文说明](README.zh-CN.md) · [Skill packages](#skill-packages) · [Quick start](#quick-start) · [Security model](#security-and-scope)

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

Keep long examples, prompts, scripts, references, and benchmark notes inside the
package that owns them.

## Validation

There is no root build step. When changing a package, validate its `SKILL.md`,
README links, scripts, and package-local references. If you use Codex's local
skill validator, run it against every changed package directory.

## Security and Scope

Do not commit API keys, model credentials, private research notes, generated
auto-research outputs, `.env` files, or local staging material. Public examples
should be small, source-attributed, and safe to redistribute.
