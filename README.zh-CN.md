# Discover Math Problems

[English](README.md) | 简体中文

`discover-math-problems` 是一个面向 AI4Math 的数学问题发现与猜想生成
Skill-as-adapter package。它让 coding agent 把模糊背景、零散笔记、失败证明尝试
和未成熟定理想法整理成 ranked problem menu、conjecture lattice、evidence ledger、
counterexample pressure、proof obligations 和可恢复的 research-state packet。

当用户还不知道应该推进哪个数学问题时，可以直接使用这个独立 Skill；不需要先安装其他
AI4Math package。

## 这个 Skill 做什么

这个独立 Skill 帮助 coding agent：

- 从模糊背景中抽取数学对象、假设、例子和未知量；
- 把候选问题排序，而不是直接锁定第一个看似合理的 theorem；
- 生成 conjecture lattice，并用 toy model、反例压力和假设边界来检查；
- 记录 evidence、uncertainty、proof obligations 和可恢复的 research-state packet。

当你有研究笔记、定义、失败证明尝试或开放式研究方向，希望 agent 先整理“值得研究什么”时，直接使用这个 Skill。

## 安装 / 加载

### 一句话安装

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
