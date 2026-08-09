# 在 OpenCode Desktop 中使用 Archon

Archon 管理 Lean 数学形式化项目，并通过 agent 执行 blueprint、规划、证明、审查、
恢复和多项目协作。

## 1. 从任意对话定位 Archon

在当前 OpenCode 项目中运行：

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" doctor "$PROJECT" --json
```

从输出取得：

```text
ARCHON_HOME = archon_home
ARCHON_BIN  = archon_bin
PROJECT     = project
```

新对话使用登记的 `ARCHON_HOME`。当前工作区作为默认 `PROJECT`，用户指定路径时
采用该路径。

## 2. 初始化项目

Archon 可以接入空目录、Lean/Lake 项目，以及包含 Markdown、LaTeX 或 PDF 材料
的目录。

```bash
"$ARCHON_BIN" init "$PROJECT" --harness opencode
```

初始化后检查：

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" doctor "$PROJECT" --json
"$ARCHON_BIN" doctor "$PROJECT" --skip-auth
```

关键项目状态：

```text
loop.harness = opencode
multilane.enabled = false
.opencode/skills/lean4/SKILL.md
.opencode/tools/archon-subagent.py
```

## 3. 建立数学依赖图

`dag` 让 agent 编写非形式化 blueprint，并通过 `\uses{}` 标注依赖关系：

```bash
"$ARCHON_BIN" dag "$PROJECT" --max-iterations 4
```

静态检查 blueprint：

```bash
"$ARCHON_BIN" blueprint-doctor "$PROJECT"
```

## 4. 运行自动形式化

核心流程为 `plan → prover → review`：

```bash
"$ARCHON_BIN" loop "$PROJECT"
"$ARCHON_BIN" loop "$PROJECT" --max-iterations 3
"$ARCHON_BIN" loop "$PROJECT" --serial
"$ARCHON_BIN" loop "$PROJECT" --focus "优先形式化 theorem foo"
```

OpenCode 补丁支持普通并行 prover。并发数量由项目配置和命令参数控制。

单条自然语言命题使用显式项目流程：

1. 在 `PROJECT/statement.md` 写入完整命题；
2. 运行 `init --harness opencode`；
3. 运行 `loop`；
4. 汇报生成的 Lean 文件和 `lake build` 结果。

## 5. 恢复与讨论

恢复中断流程：

```bash
"$ARCHON_BIN" loop "$PROJECT" --resume
"$ARCHON_BIN" loop "$PROJECT" --resume --from prover
```

`--from` 可选择 `plan`、`prover` 或 `review`。

使用完整项目上下文讨论阻塞：

```bash
"$ARCHON_BIN" discuss "$PROJECT" --harness opencode
"$ARCHON_BIN" discuss "$PROJECT" --harness opencode --focus "theorem foo"
```

## 6. 查看进度和历史

```bash
"$ARCHON_BIN" dashboard "$PROJECT" --open
"$ARCHON_BIN" log "$PROJECT" -n 30
"$ARCHON_BIN" version "$PROJECT"
```

Dashboard 使用 Node.js。终端日志、`.archon/` 状态和 inner Git 历史用于追踪每个
阶段的输入、输出和提交。

## 7. 拆分、合并与重构

提取 blueprint 依赖闭包形成子项目：

```bash
"$ARCHON_BIN" extract "$PROJECT" \
  --dest <new-project> \
  --harness opencode \
  --build
```

合并两个 Archon 项目：

```bash
"$ARCHON_BIN" merge "$PROJECT" \
  --from <source-project> \
  --dest <merged-project> \
  --harness opencode
```

生成并执行重构计划：

```bash
"$ARCHON_BIN" refactor draft "$PROJECT" --harness opencode
"$ARCHON_BIN" refactor run "$PROJECT"
```

跨项目写入前，向用户确认源目录、目标目录和预期文件变化。

## 8. 多项目协作

查看 peers 和 inbox：

```bash
"$ARCHON_BIN" peers --project-path "$PROJECT"
"$ARCHON_BIN" peers inbox --project-path "$PROJECT"
```

建立项目 scope：

```bash
"$ARCHON_BIN" scope init <scope-dir>
cd <scope-dir>
"$ARCHON_BIN" scope add '<project-path-or-glob>'
"$ARCHON_BIN" scope ls
"$ARCHON_BIN" scope graph
"$ARCHON_BIN" scope roadmap --harness opencode
"$ARCHON_BIN" scope dashboard
```

## 9. Subagent

项目配置中的 `subagents` 控制 Archon subagent。OpenCode 初始化会安装
`.opencode/tools/archon-subagent.py`，Archon 通过该 wrapper 启动子任务并等待
结果。启用前确认名称、写入范围、并发数量和 provider 额度。

## 10. 新项目对话示例

用户可以在任意 OpenCode 项目的新对话中输入：

> 使用 Archon 把当前项目中的数学说明形式化为 Lean。先检查项目状态，初始化
> OpenCode harness，然后运行 blueprint 和 loop，并持续汇报 Lean 构建结果。

Skill 应读取已登记的 `archon_home`，派生 `archon_bin`，把当前工作区设为
`PROJECT`，并根据 doctor 输出选择 `init`、`dag`、`loop` 或 `loop --resume`。

## 11. 报告内容

每次运行报告：

- Archon CLI 路径与版本；
- 当前项目路径与 harness；
- provider/model；
- 当前 phase 与迭代；
- 修改的 Lean 文件；
- `lake build` 结果；
- Dashboard、日志和项目状态路径。
