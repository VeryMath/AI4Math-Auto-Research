# Discover Math Problems

[English](README.md) | 简体中文

`discover-math-problems` 帮助 coding agent 把模糊数学背景整理成可继续推进的 research-state packet。

## 适合什么任务

当你有这些输入时使用：

- 零散笔记、定义、例子或失败证明尝试；
- 有开放式研究方向，但还没有清晰的问题排序；
- 未成熟 theorem ideas，需要先做反例压力和假设边界检查；
- 希望留下可恢复的 conjectures、evidence 和 uncertainty 记录。

## 会产出什么

Agent 应产出 ranked problem menu、conjecture lattice、evidence ledger、counterexample pressure notes、proof obligations、work orders 和 `research_state_packet`。

## 安装

把下面这句话发给你的 coding agent：

```text
请帮我安装 `discover-math-problems` skill，链接是：https://github.com/VeryMath/AI4Math-Auto-Research.git，分支：codex/discover-math-problems-skill。请读取 `.agent.md`，安装其中声明的 Skill entrypoint，验证 `$discover-math-problems` 可用，并告诉我是否需要重启 agent。
```

如果你已经有这个 skill 仓库的本地文件夹，把链接换成本地路径即可。clone、link、配置、reload/restart 检查和验证都交给 coding agent 处理。

## 快速开始

```text
Use $discover-math-problems.

我有一些背景笔记和不成熟的定理想法。请建立 research state，排序候选问题，
生成 conjecture_lattice，压力测试最有希望的候选，并产出后续 review 可用的
proof_obligations。
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
  -> 下一轮 discovery 或最终 research-state packet
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

## 维护检查

修改后先检查 Skill 形状：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/discover-math-problems
```

父级 AI4Math Skill Library 中还有 repository-level adapter checks。
