# Proof Blueprint Review

[English](README.md) | 简体中文

`proof-blueprint-review` 帮助 coding agent 围绕候选命题或证明草稿开展 proof-work session。

它不是默认 API wrapper。外部 verifier service 或模型 API 只在可用且明确有帮助时作为可选工具使用。

## 适合什么任务

当你有这些输入时使用：

- 需要明确 assumptions 和 scope 的 theorem statement；
- 需要写 proof blueprint 并检查 gaps 的 proof sketch；
- 需要 repair hints 的 proof-obligation ledger；
- 需要谨慎判断证明状态的 draft proof。

## 会产出什么

Agent 应产出 `problem_intake.md`、`proof_blueprint.md`、verifier-style review artifacts、`repair_hints.md`、proof-obligation patches 和 acceptance-gate summary。

## 安装

把下面这句话发给你的 coding agent：

```text
请帮我安装 `proof-blueprint-review` skill，链接是：https://github.com/VeryMath/AI4Math-Auto-Research.git。请读取包内 `SKILL.md`，安装其中声明的 Skill entrypoint，验证 `$proof-blueprint-review` 可用，并告诉我是否需要重启 agent。
```

如果你已经有这个 skill 仓库的本地文件夹，把链接换成本地路径即可。clone、link、配置、reload/restart 检查和验证都交给 coding agent 处理。

## 快速开始

```text
Use $proof-blueprint-review.

我有一个候选命题和 proof obligations。请先规范化 statement 和 assumptions，
再写 proof_blueprint.md，做 verifier-style review，产出 repair_hints.md 和
proof_obligation_patches.json；除非 acceptance gate 通过，不要把草稿说成 verified proof。
```

可输入 theorem statement、proof sketch、失败的证明尝试、`proof_obligations`、
verifier feedback，或已有 proof-state artifacts 目录。

## 如何交互使用

推荐使用 checkpoint 循环：

```text
候选命题或证明 artifacts
  -> problem intake
  -> proof blueprint
  -> verifier-style review
  -> repair hints and proof-obligation patches
  -> approve / revise / reject / skip
  -> 下一轮 proof iteration 或 acceptance gate
```

`approve` 表示执行下一步证明操作，`revise` 表示调整命题、路线、假设或 repair target，
`reject` 表示停止当前证明路线，`skip` 表示跳过非必要阶段。Agent 在修改 theorem
statement、接受 black box、放弃用户偏好的路线、启动外部 verifier、或声称 proof
accepted 之前，都应该先询问用户。

## 产物合同

实质性证明工作应创建或更新：

- `problem_intake.md`
- `proof_blueprint.md`
- `generation_trace.json`
- `verification_report.json`
- `verification_summary.md`
- `repair_hints.md`
- `proof_obligation_patches.json`
- `acceptance_gate.md`

只有 theorem statement 匹配、assumptions 和 black boxes 明确、存在等价于
`verdict="correct"` 的 verifier-style 或 human review evidence、且没有未解决的
`critical_errors` 和 `gaps` 时，才能报告为 accepted。这个状态应称为
`accepted_by_review`，不自动等于 verified。只有外部 verifier/prover 接受并记录证据时才用
`externally_verified`；只有 Lean 等 proof assistant 检查最终证明时才用 `machine_checked`。

## 维护检查

修改后先检查 Skill 形状：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/proof-blueprint-review
```

父级 AI4Math Skill Library 中还有 repository-level adapter checks。
