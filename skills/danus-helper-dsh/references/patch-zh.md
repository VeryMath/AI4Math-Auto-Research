# 应用 Danus DeepSeek Harness 适配

本补丁面向 Danus release `v0.1.0-codex` 的 commit
`7a51336e53cd1d558d0e766a61eb0fed46ebb05b`，适配 DeepSeek Harness
`0.1.0-rc.5` 与 `0.1.0-rc.6`。

## 1. 检查状态

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-status --json
```

状态含义：

- `not-installed`：源码位于受支持的基线，补丁能够应用；
- `installed`：完整补丁已经存在；
- `installed-modified`：适配文件在安装后发生了变化；
- `conflict-or-partial`：工作区包含冲突或局部适配，需要检查具体文件。

应用前检查：

```bash
git -C "$DANUS_HOME" rev-parse HEAD
git -C "$DANUS_HOME" status --short
```

## 2. 应用补丁

向用户说明源码修改范围。用户确认后运行：

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-apply --json
```

helper 会核对 commit、检查工作区、执行 `git apply --check`、应用补丁、编译 Python
源码、运行 `git diff --check`，最后再次读取补丁状态。检查发生错误时，helper 会反向
应用本次补丁，让仓库回到受支持的基线。

随后运行：

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-status --json
git -C "$DANUS_HOME" diff --check
```

预期 `patch_state` 为 `installed`。

## 3. 适配范围

补丁包含以下运行链路：

- DeepSeek Harness Web 主 agent 和 Danus 项目指令；
- DeepSeek Harness headless worker、验证 agent、策略咨询和论文写作；
- Danus、write-paper、human-summary 三个 MCP 服务；
- 并行 worker、事实图、证明验证、反馈和修订；
- DeepSeek Harness 官方 `schedule_create`、`schedule_list`、`schedule_delete` 工具；
- worker 进程清理、轮次接续、服务登记和主机重启恢复；
- 长论文的规划、分章生成、LaTeX 编译、引用检查和数学验证；
- 中文或英文进展总结及 PDF 渲染。

主 agent 运行在 DeepSeek Harness Web。其他模型任务通过 headless profile 创建独立
会话。worker 的研究记忆、事实图、任务文件和轮次日志保存在 Danus 项目目录中。

## 4. 移除补丁

先停止 Danus worker 和服务，再运行：

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-remove --json
```

helper 会检查活动进程和反向补丁条件。完成后的 `patch_state` 为 `not-installed`。
`installed-modified` 表示相关文件已经变化，需要先查看这些改动。

## 5. 处理冲突

遇到 `conflict-or-partial` 时读取：

```bash
git -C "$DANUS_HOME" status --short
git -C "$DANUS_HOME" apply --check "$SKILL_DIR/assets/danus-v0.1.0-codex-dsh.patch"
```

向用户报告冲突文件，保留现有改动，并请用户决定使用新的干净安装目录或人工合并。
