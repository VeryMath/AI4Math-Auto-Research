# 在 OpenCode Desktop 中使用 Danus

Danus 的主 agent、skills、MCP 服务、定时插件和研究状态都位于已登记的
`DANUS_HOME`。从任意新项目或新对话调用 `$danus-helper` 时，先读取安装记录，再
根据请求进入研究、监控、恢复、进展总结或论文写作流程。

## 1. 找到安装和现有项目

先运行：

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" installation-show --json
python3 "$SKILL_DIR/scripts/danus_helper.py" doctor --json
```

把返回的 `danus_home` 记为 `DANUS_HOME`。随后查看现有项目：

```bash
cd "$DANUS_HOME"
bin/danus list
```

向用户报告安装路径、部署状态和现有项目。新研究任务需要在 OpenCode Desktop 中
打开 `DANUS_HOME`；OpenCode 将从该目录加载 Danus 的 `AGENTS.md`、skills、MCP
服务和定时插件。首次访问该目录时，OpenCode 可能请求
`external_directory` 权限。

## 2. 开始数学研究

用户可以直接给出原始问题，例如：

```text
用 Danus 研究这个问题：设 X 和 Y 是 Banach 空间，证明闭图定理，并完整给出从
Baire 范畴定理推出开映射定理的逐次逼近论证。
```

保留用户给出的数学命题和全部条件。新部署先调用 Danus 的 `initialize` skill，
记录语言、工作分支、费用提醒和 worker 数量等偏好。首次模型调用前，agent 报告
provider 和 model，并请求用户确认。用户确认后，Danus 主 agent 按项目合约完成：

1. 保存原始问题并创建项目；
2. 获取研究策略；
3. 分配并启动 OpenCode workers；
4. 接收验证 agent 检查后的数学事实；
5. 根据事实图和验证意见调整任务；
6. 定期汇报进展；
7. 提交候选结论，请用户确认最终目标。

研究数据保存在：

```text
$DANUS_HOME/runtime/projects/<project>/
```

## 3. 定时检查和 Desktop 重启

worker 启动后，主 agent 使用 `danus_schedule_wakeup` 登记下一次项目检查。每次检查
结束后，根据项目状态登记新的间隔。用户明确要求固定提醒时，使用 `/loop`；
`/loop-list` 查看当前会话的任务，`/loop-stop` 结束固定提醒。

worker 作为独立进程继续运行，OpenCode Desktop 退出期间仍可推进证明。会话定时
插件随 Desktop 项目运行。重新打开 `DANUS_HOME` 后执行：

```bash
bin/danus list
bin/danus status <project>
```

读取当前进度，在新会话中为仍需监控的项目登记下一次检查。已错过的检查会在会话
恢复空闲后合并处理。

## 4. worker 崩溃和主机重启

worker 状态异常时先检查：

```bash
bin/danus status <project>
```

随后重新启动项目：

```bash
bin/danus start <project>
```

启动逻辑会清理崩溃 worker 遗留的 OpenCode 子进程，并从现有项目记忆、事实图和
下一轮日志编号继续运行。

主机重启后执行：

```bash
bash scripts/recover.sh
bash scripts/services.sh status
```

恢复脚本重建运行环境并恢复已登记的共享服务。然后查看项目状态，经用户确认后用
`bin/danus start <project>` 恢复相应 workers，并在当前会话登记下一次检查。

## 5. 生成人类可读的进展总结

总结可以在研究过程的任意阶段生成。先完整读取：

```text
$DANUS_HOME/.claude/skills/human-summary/SKILL.md
```

按照其中的流程调用 `human-summary` MCP 的 `summary_write`，传入项目名和用户语言。
检查返回的 `status`、Markdown 路径、PDF 路径和内容检查结果。交付前确认 PDF 文件
存在且能够打开，并向用户报告总结覆盖的研究阶段。

macOS 标准安装位置中的 Google Chrome 和 Chromium 会被自动识别。诊断命令为：

```bash
bash scripts/doctor.sh
```

## 6. 生成完整论文

论文流程需要用户确认目标事实。先检查候选目标，并根据用户决定登记：

```bash
bin/danus finalize <project>
bin/danus finalize <project> <fact_id> [<fact_id> ...]
```

随后完整读取：

```text
$DANUS_HOME/.claude/skills/write-paper/SKILL.md
```

按照该 skill 完成事实选择、论文生成、LaTeX 编译、参考文献检查、引用核实、数学
验证和必要修订。长论文由写作流程规划章节并分段生成。结束时报告：

- 最终 `main.tex` 和 PDF 的绝对路径；
- 编译结果；
- 引用检查与核实结果；
- 数学验证结论；
- 当前 worker 状态。

论文流程涉及停止 workers、作者信息、投稿或推送操作时，先取得用户决定。

## 7. 诊断入口

按症状读取对应信息：

| 现象 | 检查位置 |
|---|---|
| OpenCode 调用退出 | `runtime/logs/opencode.log`、worker 的 `logs/round_*.log` |
| 数学事实提交失败 | `runtime/logs/verify.log`、`runtime/verify-runs/` |
| MCP 工具缺失 | `opencode mcp list`、`bash scripts/doctor.sh` |
| 定时检查未出现 | `/loop-list`、`runtime/opencode-loops.json` |
| 论文或总结失败 | MCP 返回的 `log_path` 和对应项目工作目录 |

自定义 provider 的美元费用依赖其模型定价信息。token 用量仍可从 OpenCode JSON
事件和 `opencode stats` 中读取。
