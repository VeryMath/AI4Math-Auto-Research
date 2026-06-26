<div align="center">

# AI4Math · 自动研究

面向数学问题发现、研究循环编排和证明蓝图审查的 agentic workflow 技能集合。

[English](README.md) · [技能包](#技能包) · [快速开始](#快速开始) · [安全边界](#安全边界)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-3-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

## 这个仓库是什么

这个仓库是 AI4Math 自动研究方向的技能入口，收集用于把模糊数学意图转成结构化问题、有限预算研究运行和可复核证明计划的 Skill-as-adapter 包。

根 README 负责说明地图；真正执行任务时，请进入对应的 `skills/` 子目录。

## 技能包

| 包 | 适用任务 | 入口 |
| --- | --- | --- |
| [`agent-laboratory-workflow`](skills/agent-laboratory-workflow/) | 部署、验证并启动有边界的 Agent Laboratory 自动研究运行。 | [`README`](skills/agent-laboratory-workflow/README.md) · [`SKILL`](skills/agent-laboratory-workflow/SKILL.md) |
| [`discover-math-problems`](skills/discover-math-problems/) | 把模糊背景转为候选问题、猜想格、证据台账和后续工作单。 | [`README`](skills/discover-math-problems/README.md) · [`SKILL`](skills/discover-math-problems/SKILL.md) |
| [`proof-blueprint-review`](skills/proof-blueprint-review/) | 生成证明蓝图、执行 verifier-style review、记录修复提示并给出严格证明状态。 | [`README`](skills/proof-blueprint-review/README.md) · [`SKILL`](skills/proof-blueprint-review/SKILL.md) |

## 快速开始

克隆仓库并选择技能包：

```bash
git clone https://github.com/VeryMath/AI4Math-Auto-Research.git
cd AI4Math-Auto-Research
```

问题发现从这里开始：

```text
skills/discover-math-problems/SKILL.md
```

证明计划审查从这里开始：

```text
skills/proof-blueprint-review/SKILL.md
```

Agent Laboratory 运行从这里开始：

```text
skills/agent-laboratory-workflow/SKILL.md
```

## 仓库结构

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

长示例、提示词、脚本、references 和 benchmark notes 应放在所属技能包内。

## 验证

这个仓库没有根级构建步骤。修改技能包后，请检查 `SKILL.md`、README 链接、脚本和包内 references；如果使用 Codex 本地 skill validator，请对每个变更包目录运行验证。

## 安全边界

不要提交 API key、模型凭证、私有研究笔记、自动研究生成输出、`.env` 文件或本地 staging material。公开示例应尽量小、来源清楚，并确认可以再分发。
