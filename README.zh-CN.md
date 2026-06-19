# Discover Math Problems

[English](README.md) | 简体中文

`discover-math-problems` 是一个面向 AI4Math 的数学问题发现与猜想生成
Skill-as-adapter package。它让 coding agent 把模糊背景、零散笔记、失败证明尝试
和未成熟定理想法整理成 ranked problem menu、conjecture lattice、evidence ledger、
counterexample pressure、proof obligations 和可恢复的 research-state packet。

当用户还不知道应该推进哪个数学问题时，先用这个 Skill；进入证明阶段后，再交给
`rethlas-proving`。

## AI4Math 角色

这个 Skill 是 AI4Math 体系里的猜想生成和 research-state 层。它把背景知识整理成候选问题、
conjecture lattices、evidence ledgers、counterexample pressure 和 proof obligations，
然后再交给证明或形式化 Skill 去尝试认证。

## 安装 / 加载

优先从 checkout 使用。让 coding agent 读取：

```text
AGENTS.md
SKILL.md
```

如果目标 agent 支持本地 Skill discovery，可以把本目录安装或软链接到它的 Skill
路径，然后按需 reload 或 restart。

Codex 示例：

```bash
ln -s "$PWD/skills/discover-math-problems" ~/.codex/skills/discover-math-problems
```

Codex、Claude、Gemini 和 OpenCode 的薄 adapter 分别见 `.codex/INSTALL.md`、
`CLAUDE.md`、`GEMINI.md` 和 `.opencode/INSTALL.md`。

## 快速开始

```text
Use $discover-math-problems.

我有一些背景笔记和不成熟的定理想法。请建立 research state，排序候选问题，
生成 conjecture_lattice，压力测试最有希望的候选，并产出可以交给 theorem proving
的 proof_obligations。
```

可输入研究方向背景、source notes、definitions、examples、失败证明尝试、开放式研究目标，
或已经形成一半的 conjectures。

## 如何交互使用

推荐使用 checkpoint 循环：

```text
背景或未成熟想法
  -> background map
  -> problem menu
  -> conjecture lattice
  -> evidence ledger and counterexample pressure
  -> proof obligations
  -> approve / revise / reject / skip
  -> 交给 proving 或进入下一轮 discovery
```

`approve` 表示执行下一步发现操作，`revise` 表示调整领域、假设、source scope 或候选排序，
`reject` 表示停止当前方向，`skip` 表示跳过非必要阶段。Agent 在改变中心数学对象、
接受强外部定理作为 black box、放弃用户偏好的方向、长时间执行 source acquisition
或 computational search、以及把候选提升到 `verification_ready` 之前，都应该先询问用户。

## 产物合同

实质性 discovery 工作应创建或更新：

- `background_map.md` and `background_map.json`
- `problem_menu.md` and `problem_menu.json`
- `conjecture_lattice.md` and `conjecture_lattice.json`
- `evidence_ledger.json`
- `counterexample_pressure.md`
- `proof_obligations.md` and `proof_obligations.json`
- `work_orders.md` and `work_orders.json`
- `research_state_packet.json`
- `human_decision_brief.md`

状态标签要诚实使用：`background_map`、`candidate_problem_menu`、
`candidate_conjecture`、`stress_tested_conjecture`、`proof_obligations_ready`
或 `verification_ready`。`verification_ready` 的意思是“可以进入验证工作”，不是已经
verified。不要把 conjecture 叫成 theorem。

## 交接

当候选达到 `proof_obligations_ready` 或 `verification_ready`，把 obligation packet
交给 `rethlas-proving`，由它负责 proof blueprint、verifier-style review、
repair hints 和 acceptance gate。

不变量或反例证据任务交给 `invariant-computation`；优化型任务交给
`optimization-modeling` 或 `cdopt-optimization`；实验型检查交给
`scientific-computing-reproduction`；有明确 evaluator 和 metric 的搜索交给
`openevolve-experiment-workflow`。

## 维护检查

修改后先检查 Skill 形状：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/discover-math-problems
```

父级 AI4Math Skill Library 中还有 repository-level adapter checks。
