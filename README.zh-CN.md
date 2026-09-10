<div align="center">

# AI4Math · 自动研究

面向数学问题发现、研究循环编排和证明蓝图审查的 agentic workflow 技能集合。

[English](README.md) · [贡献者](CONTRIBUTORS.md) · [技能包](#技能包) · [安装](#安装) · [快速开始](#快速开始) · [参考资料](#相关公开参考资料) · [安全边界](#安全边界)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-9-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

<p align="center">
  如果这个项目对你有帮助，欢迎为仓库点 Star ⭐
  <a href="https://github.com/VeryMath/AI4Math-Auto-Research"><img alt="GitHub Stars" src="https://img.shields.io/github/stars/VeryMath/AI4Math-Auto-Research?style=social"></a>
</p>

## 这个仓库是什么

这个仓库是 AI4Math 自动研究方向的技能入口，收集用于把模糊数学意图转成结构化问题、有限预算研究运行和可复核证明计划的 Skill-as-adapter 包。

根 README 负责说明地图；真正执行任务时，请进入对应的 `skills/` 子目录。

## 技能包

| 包 | 适用任务 | 入口 |
| --- | --- | --- |
| [`agent-laboratory-workflow`](skills/agent-laboratory-workflow/) | 部署、验证并启动有边界的 Agent Laboratory 自动研究运行。 | [`README`](skills/agent-laboratory-workflow/README.md) · [`SKILL`](skills/agent-laboratory-workflow/SKILL.md) |
| [`discover-math-problems`](skills/discover-math-problems/) | 把模糊背景转为候选问题、猜想格、证据台账和后续工作单，包含极值图论问题变体。 | [`README`](skills/discover-math-problems/README.md) · [`SKILL`](skills/discover-math-problems/SKILL.md) |
| [`proof-blueprint-review`](skills/proof-blueprint-review/) | 生成证明蓝图、执行 verifier-style review、记录修复提示并给出严格证明状态。 | [`README`](skills/proof-blueprint-review/README.md) · [`SKILL`](skills/proof-blueprint-review/SKILL.md) |
| [`rethlas-helper`](skills/rethlas-helper/) | 为 OpenCode 安装 Rethlas、记录本机路径，并从任意 OpenCode 项目运行自然语言证明生成。 | [`SKILL`](skills/rethlas-helper/SKILL.md) |
| [`archon-helper`](skills/archon-helper/) | 为 OpenCode 安装 Archon、记录本机路径，并从任意 OpenCode 项目运行形式化工作流。 | [`SKILL`](skills/archon-helper/SKILL.md) |
| [`danus-helper`](skills/danus-helper/) | 为 OpenCode 安装 Danus、记录本机路径，并运行多 agent 数学研究、定时检查、进展总结和论文写作。 | [`SKILL`](skills/danus-helper/SKILL.md) · [`安装介绍`](docs/danus-helper-setup.md) · [`使用例子`](docs/danus-closed-graph-example.md) |
| [`danus-helper-dsh`](skills/danus-helper-dsh/) | 为 DeepSeek Harness 安装 Danus、记录本机路径，并运行同一套数学研究、验证、总结和论文流程。 | [`SKILL`](skills/danus-helper-dsh/SKILL.md) · [`安装介绍`](docs/danus-helper-setup.md) · [`使用例子`](docs/danus-closed-graph-example.md) |
| [`graph-theory-researcher`](skills/graph-theory-researcher/) | 阅读图论论文，通过用户检查点选择问题，开展有边界研究并生成可核验 LaTeX/PDF。 | [`README`](skills/graph-theory-researcher/README.md) · [`SKILL`](skills/graph-theory-researcher/SKILL.md) |
| [`open-problem-research-pipeline`](skills/open-problem-research-pipeline/) | 对数学公开问题执行文献搜索、方法分析、证明框架和报告组装的分阶段流程。 | [`README`](skills/open-problem-research-pipeline/README.md) · [`SKILL`](skills/open-problem-research-pipeline/SKILL.md) |

## 安装

推荐方式是 AI 自动安装：让你的 coding agent 自己 clone 或更新仓库、读取 Skill 说明、安装入口并验证 discovery。

```text
请帮我安装这些 AI4Math Skills。

仓库：https://github.com/VeryMath/AI4Math-Auto-Research.git
分支：main
Skill 路径：
- skills/agent-laboratory-workflow
- skills/discover-math-problems
- skills/proof-blueprint-review
- skills/rethlas-helper
- skills/archon-helper
- skills/danus-helper
- skills/danus-helper-dsh
- skills/graph-theory-researcher
- skills/open-problem-research-pipeline

请执行：
1. 本地 clone 或更新仓库。
2. 读取 README.md、SKILL.md、AGENTS.md（如果存在）以及每个目标 Skill 入口。
3. 如果当前环境支持本地 Skill discovery，把每个包含 SKILL.md 的目录链接到本地 skills 目录。
4. 如果某个 Skill 依赖相邻的共享支持目录，请保留这些 sibling 目录。
5. 验证安装后的 Skills 是否可被发现。
6. 告诉我安装路径、是否需要重启 agent，并给我一个测试 prompt。
```

Codex 风格本地 discovery 的手工 fallback：

```bash
git clone https://github.com/VeryMath/AI4Math-Auto-Research.git
cd AI4Math-Auto-Research
mkdir -p ~/.codex/skills
ln -s "$PWD/skills/agent-laboratory-workflow" ~/.codex/skills/agent-laboratory-workflow
ln -s "$PWD/skills/discover-math-problems" ~/.codex/skills/discover-math-problems
ln -s "$PWD/skills/proof-blueprint-review" ~/.codex/skills/proof-blueprint-review
ln -s "$PWD/skills/rethlas-helper" ~/.codex/skills/rethlas-helper
ln -s "$PWD/skills/archon-helper" ~/.codex/skills/archon-helper
ln -s "$PWD/skills/danus-helper" ~/.codex/skills/danus-helper
ln -s "$PWD/skills/danus-helper-dsh" ~/.codex/skills/danus-helper-dsh
ln -s "$PWD/skills/graph-theory-researcher" ~/.codex/skills/graph-theory-researcher
ln -s "$PWD/skills/open-problem-research-pipeline" ~/.codex/skills/open-problem-research-pipeline
```

如果你的 agent 使用别的本地 Skill 目录，把 `~/.codex/skills` 替换成对应配置路径。

OpenCode Desktop 从 `~/.config/opencode/skills` 发现全局 Skill。使用以下命令
安装 Rethlas Helper、Archon Helper 和 Danus Helper：

```bash
mkdir -p ~/.config/opencode/skills
ln -s "$PWD/skills/rethlas-helper" ~/.config/opencode/skills/rethlas-helper
ln -s "$PWD/skills/archon-helper" ~/.config/opencode/skills/archon-helper
ln -s "$PWD/skills/danus-helper" ~/.config/opencode/skills/danus-helper
```

DeepSeek Harness 使用 `danus-helper-dsh`。让 agent 安装 Skill、部署 Danus 和登记路径
的完整提示词见 [Danus 安装介绍](docs/danus-helper-setup.md)。

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

Rethlas 的持久化安装、跨项目定位和 OpenCode 解题流程从这里开始：

```text
skills/rethlas-helper/SKILL.md
```

Archon 的持久化安装、跨项目定位和 OpenCode 形式化流程从这里开始：

```text
skills/archon-helper/SKILL.md
```

Danus 的 OpenCode 与 DeepSeek Harness 安装、多 agent 数学研究、定时检查、进展
总结和论文生成流程从这里开始：

```text
skills/danus-helper/SKILL.md
skills/danus-helper-dsh/SKILL.md
```

两种运行环境共用[安装介绍](docs/danus-helper-setup.md)和
[闭图像定理使用示例](docs/danus-closed-graph-example.md)。

课程贡献的图论与公开问题工作流从这里开始：

```text
skills/graph-theory-researcher/SKILL.md
skills/open-problem-research-pipeline/SKILL.md
```

极值图论选题使用 `discover-math-problems` 及其
[问题变体清单](skills/discover-math-problems/references/extremal-graph-variants.md)。
[完整旧包已存档](archives/README.md)，保留贡献者记录和许可证。

## 仓库结构

```text
AI4Math-Auto-Research/
├── README.md
├── README.zh-CN.md
├── SKILL.md
├── archives/
└── skills/
    ├── agent-laboratory-workflow/
    ├── discover-math-problems/
    ├── proof-blueprint-review/
    ├── rethlas-helper/
    ├── archon-helper/
    ├── danus-helper/
    ├── danus-helper-dsh/
    ├── graph-theory-researcher/
    └── open-problem-research-pipeline/
```

技能包自己的长示例、提示词、脚本、references 和 benchmark notes 应放在所属技能包内。

## 验证

运行：

```bash
python3 -m unittest discover -s tests -v
bash skills/graph-theory-researcher/scripts/validate-skill.sh
```

如果使用 Codex 本地 skill validator，请对每个变更包目录运行验证。

## 相关公开参考资料

相关公开参考资料：

- [Agent Laboratory](https://github.com/SamuelSchmidgall/AgentLaboratory)
- [Rethlas](https://github.com/frenzymath/Rethlas)
- [Automated Conjecture Resolution with Formal Verification](https://arxiv.org/abs/2604.03789)
- [Archon](https://github.com/frenzymath/Archon)
- [Danus](https://github.com/frenzymath/Danus)
- [Danus：使用事实图记忆编排数学推理 agents](https://arxiv.org/abs/2607.06447)
- [LeanSearch](https://github.com/frenzymath/LeanSearch)

## 安全边界

不要提交 API key、模型凭证、私有研究笔记、自动研究生成输出、`.env` 文件或本地 staging material。公开示例应尽量小、来源清楚，并确认可以再分发。
