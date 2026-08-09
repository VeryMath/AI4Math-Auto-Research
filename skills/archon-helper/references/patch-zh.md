# 安装 Archon OpenCode 补丁

本阶段从已登记的 `archon_home` 检查并应用 Archon 0.3.3 OpenCode 补丁。

## 1. 检查安装与补丁状态

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" installation-show --json
python3 "$SKILL_DIR/scripts/archon_helper.py" patch-status --json
```

确认：

- `version` 为 `0.3.3`；
- `archon_home` 指向预期源码；
- `patch_state` 为 `not-installed` 或 `installed`；
- Archon 源码中的现有改动已经向用户报告。

`conflict-or-partial` 表示源码与补丁存在冲突或局部应用，需要检查 Git 输出和
涉及文件。

## 2. 应用补丁

用户批准 Archon 源码修改后运行：

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" patch-apply
```

helper 执行以下工作：

1. 检查 Archon 版本；
2. 检查工作区状态；
3. 运行 `git apply --check`；
4. 应用 OpenCode 补丁；
5. 编译 `src/archon`；
6. 确认完整补丁状态。

完成后再次运行：

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" patch-status --json
```

预期状态为 `installed`。

## 3. 补丁提供的能力

补丁注册 OpenCode harness，覆盖：

- `init` 的项目文件安装；
- `plan`、`prover` 和 `review`；
- `loop --resume`；
- Archon subagent；
- `dag`、`discuss`、`extract`、`merge` 和 `refactor` 等 agent 命令；
- Lean-LSP MCP 注入；
- OpenCode session 记录与恢复。

OpenCode 项目使用普通并行 prover。`multilane.enabled` 设置为 `false`。

## 4. 初始化当前项目

新项目运行：

```bash
"$ARCHON_BIN" init "$PROJECT" --harness opencode
```

已有 Archon 项目需要补齐 OpenCode 项目文件时，先检查现有 `.archon/` 配置和
Git 状态，再向用户说明 re-init 影响。

初始化产生：

```text
$PROJECT/.opencode/skills/lean4/SKILL.md
$PROJECT/.opencode/tools/archon-subagent.py
```

随后运行：

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" doctor "$PROJECT" --json
"$ARCHON_BIN" doctor "$PROJECT" --skip-auth
cd "$PROJECT"
lake build
```

## 5. 已知范围

- OpenCode 工作流使用显式 `init --harness opencode` 和 `loop` 完成单命题任务；
- Archon 0.3.3 的 `prove` 快捷命令内部 init 沿用默认 harness；
- `archon setup` 面向上游 Claude Code 环境；
- `archon update` 会改变补丁对应的源码版本；
- `multilane` 的 lane runner 与 merge agent 使用上游 Claude 组件。

报告 `archon_home`、CLI 路径、版本、补丁状态、当前项目 harness、Lean 构建状态
和下一条形式化命令。
