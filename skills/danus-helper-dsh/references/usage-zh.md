# 使用 Danus DeepSeek Harness 适配版

Danus 的主 agent、研究 Skills、MCP 服务和项目状态位于已登记的 `DANUS_HOME`。
`danus-helper-dsh` 通过 `$DSH_HOME/danus-helper-dsh.toml` 找到这套安装。

## 1. 打开 Danus

先读取安装状态：

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" installation-show --json
python3 "$SKILL_DIR/scripts/danus_helper.py" doctor --json
```

服务运行后，在浏览器打开：

```text
http://127.0.0.1:3080
```

需要启动服务时运行：

```bash
cd "$DANUS_HOME"
bash scripts/services.sh up verify
```

查看已有项目：

```bash
cd "$DANUS_HOME"
bin/danus list
```

## 2. 开始数学研究

用户可以直接提交完整命题，例如：

```text
用 Danus 研究这个问题：设 X 和 Y 是 Banach 空间，证明闭图定理，并完整给出从
Baire 范畴定理推出开映射定理的逐次逼近论证。
```

首次模型调用前，agent 会报告 provider 和 model，并请求用户确认。确认后，Danus
依次保存原始问题、建立项目、取得研究策略、分配 worker、验证数学事实、根据验证
意见修订方向，并持续汇报进展。

研究数据保存在：

```text
$DANUS_HOME/runtime/projects/<project>/
```

常用检查命令：

```bash
bin/danus status <project>
bin/danus list --json
```

## 3. 定时检查

主 agent 使用 DeepSeek Harness 官方调度工具登记后续检查：

- `schedule_create`：创建一次性或重复检查；
- `schedule_list`：查看当前会话的计划；
- `schedule_delete`：结束计划。

这些计划属于创建它们的 DeepSeek Harness 会话。Web 服务保持运行时，计划会按时
唤醒会话。服务重新启动并恢复同一会话后，已到期的计划会继续投递。Danus 的 worker
运行在独立进程中，研究进度同时写入项目目录。

## 4. 恢复运行

worker 状态异常时运行：

```bash
bin/danus status <project>
bin/danus start <project>
```

重新启动项目时，Danus 会清理遗留子进程，并依据项目记忆、事实图和现有轮次编号
继续运行。

主机重启后运行：

```bash
cd "$DANUS_HOME"
bash scripts/recover.sh
bash scripts/services.sh status
```

随后查看项目状态，启动仍需推进的 worker，并在恢复的会话中登记下一次检查。

## 5. 生成人类可读的进展总结

完整读取：

```text
$DANUS_HOME/.agents/skills/human-summary/SKILL.md
```

按其中流程调用 `mcp__human-summary__summary_write`，传入项目名和用户语言。检查返回的
Markdown 路径、PDF 路径和内容检查结果。交付时报告文件绝对路径与总结覆盖的研究
阶段。

PDF 渲染使用 Google Chrome 或 Chromium。诊断命令为：

```bash
bash scripts/doctor.sh
```

## 6. 生成完整论文

先检查候选目标，并按用户决定登记：

```bash
bin/danus finalize <project>
bin/danus finalize <project> <fact_id> [<fact_id> ...]
```

随后完整读取：

```text
$DANUS_HOME/.agents/skills/write-paper/SKILL.md
```

写作流程覆盖事实选择、论文规划、分章生成、LaTeX 编译、参考文献检查、引用核实、
数学验证和修订。结束时报告 `main.tex`、PDF 和日志的绝对路径，以及编译、引用和
数学验证结果。

## 7. 诊断入口

| 现象 | 检查位置 |
|---|---|
| DeepSeek Harness Web 启动异常 | `runtime/logs/dsh.log` |
| worker 回合退出 | `runtime/projects/<project>/workers/<worker>/logs/` |
| 数学事实提交失败 | `runtime/logs/verify.log`、`runtime/verify-runs/` |
| MCP 工具加载失败 | `bash scripts/check-dsh.sh`、`bash scripts/doctor.sh` |
| 定时检查未出现 | DeepSeek Harness 会话中的 `schedule_list` |
| 论文或总结失败 | MCP 返回的 `log_path` 和对应项目工作目录 |

DeepSeek Harness headless 的最终文本记录在各任务日志中。Danus 同时记录所用模型和
回合状态。
