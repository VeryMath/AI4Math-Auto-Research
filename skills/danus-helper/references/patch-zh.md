# 应用 Danus OpenCode 适配

本阶段把 Danus release `v0.1.0-codex` 的 commit
`7a51336e53cd1d558d0e766a61eb0fed46ebb05b`
转换为经过测试的 OpenCode 版本。

## 1. 检查状态

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-status --json
```

状态含义：

- `not-installed`：源码位于支持基线，补丁能够应用；
- `installed`：完整补丁已经存在；
- `installed-modified`：适配已经存在，安装后又修改了适配文件；
- `conflict-or-partial`：源码包含冲突或局部适配，需要检查工作区。

应用前同时确认：

```bash
git -C "$DANUS_HOME" rev-parse HEAD
git -C "$DANUS_HOME" status --short
```

## 2. 应用补丁

向用户说明将修改 Danus 源码。获得批准后运行：

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-apply --json
```

helper 会核对支持的 commit、检查工作区、执行 `git apply --check`、应用补丁、编译
Python 源码、运行 `git diff --check`，并再次检查补丁状态。应用后的检查发生错误
时，helper 会反向应用补丁，让仓库回到受支持的基线。

随后运行：

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-status --json
git -C "$DANUS_HOME" diff --check
```

预期 `patch_state` 为 `installed`。

## 3. 适配提供的功能

补丁覆盖 Danus 的完整 OpenCode 运行链路：

- OpenCode Desktop 主 agent 与项目级 `AGENTS.md`；
- OpenCode worker、验证 agent、策略咨询和论文写作；
- 共享 OpenCode Server 与独立 session；
- 并行 worker、事实图、验证反馈和修订；
- 服务恢复、session 记录、token 与费用记录；
- OpenCode `/loop` 命令和会话内定时唤醒；
- worker 崩溃后的进程组清理和轮次接续；
- Danus、write-paper 与 human-summary MCP 服务；
- 长论文的规划、分章生成、编译、引用检查和数学验证；
- 中文或英文进展总结及 PDF 渲染。

补丁应用后，源码改动保留在安装分支中。用户可以在检查完成后自行提交该部署分支。

需要回到受支持的上游基线时，先停止 Danus workers 和服务，再运行：

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-remove --json
```

helper 会先确认完整补丁能够反向应用。结束后的 `patch_state` 应为
`not-installed`。`installed-modified` 表明安装后的文件已经发生修改，先检查这些
改动，再决定保留改动或人工还原。

## 4. 冲突处理

遇到 `conflict-or-partial` 时，读取 `git status --short` 和
`git apply --check` 的错误位置。保留用户已有改动，向用户说明冲突文件，再等待其
选择新的干净安装目录或人工合并方案。
