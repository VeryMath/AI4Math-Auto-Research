---
name: archon-helper
description: 安装或 clone Archon，检测原版 Claude Code 运行环境是否可用，引导用户配置自己的 Claude/OpenCode provider 和模型，按用户选择应用 OpenCode 兼容补丁，并介绍、运行或排查 Archon 的各项功能。用于安装 Archon、配置 Python/Lean/uv/agent 环境、选择原版 Claude Code 或 OpenCode、迁移已有项目，以及使用 init/dag/loop/discuss/resume/extract/merge/refactor/scope/subagent 等功能。
---

# Archon Helper

带用户完成四件事：安装 Archon、选定运行器、配置环境、开始使用。根据用户当前
情况往下走，别把整份检查清单一次性丢给用户。始终分清两个目录：

- `<archon-dir>`：Archon CLI 的源码检出；
- `<project>`：用户要形式化的 Lean/Archon 项目。

## 1. 先把 Archon 装好

阅读
[安装与 clone 流程](references/install-zh.md)。

先看看用户本机有没有 Archon 源码或可用的 `archon`。需要 clone 时，告诉用户
准备放在哪里、使用哪个上游版本，再执行网络操作。保留已有目录和改动；后续固定
使用 `<archon-dir>/.venv/bin/archon`，避免误用系统里的另一份 Archon。

源码准备好以后，先别急着打补丁，接着判断用户该走原版 Claude Code 还是
OpenCode。

## 2. 先问清楚这次用 Claude Code 还是 OpenCode

先实际检查：

```bash
command -v claude
claude --version
test -f <archon-dir>/src/archon/agents/opencode.py
```

然后按检测结果跟用户说：

- **没有 Claude Code，也没有补丁：**

  > 原版 Archon 0.3.3 通过 Claude Code 运行 agent，但当前没有检测到可用的
  > Claude Code。安装 OpenCode 兼容补丁后，核心 agent 和 subagent 会改由
  > OpenCode 执行。要安装这个补丁吗？

  如果用户不装，说明 agent 流程目前还跑不起来，并询问是否需要引导安装
  Claude Code。

- **已经有可用的 Claude Code，但还没有补丁：**

  > 已检测到可用的 Claude Code。你想直接使用原版 Archon，还是安装 OpenCode
  > 兼容补丁？

- **OpenCode 补丁已经安装：**

  直接报告补丁已存在，不再问要不要安装。如果 Claude Code 也可用，询问这次想
  用 Claude Code 还是 OpenCode；如果 Claude Code 不可用，就确认继续使用
  OpenCode。

用户已经明确选过运行器时，不重复问。先记住这次选择，后面的环境配置和 Archon
命令都跟着这个选择走。

## 3. 陪用户把环境配好

阅读
[环境配置流程](references/environment-zh.md)。

先检测 Python、Git、Lean/Elan/Lake、uv 和所选运行器，再告诉用户哪些已经就绪、
哪些还缺。不要只报一串命令；每遇到一个需要用户决定的地方，解释用途后再问。

- 选择原版时，引导用户完成自己的 Claude Code 登录。
- 选择 OpenCode 时，引导用户用 `opencode auth login` 连接自己的订阅或 API
  provider，并从可用模型中选择。不要替用户默认选择 DeepSeek 或任何其他
  provider/model。
- 不索取或显示密钥。安装全局工具、启动登录或发起付费模型请求前先问用户。

## 4. 用户选择 OpenCode 时再打补丁

选择原版 Claude Code 时跳过这一步。选择 OpenCode，且补丁尚未安装时，阅读
[补丁确认、应用与验证](references/patch-zh.md)。

先运行兼容性检查，再应用补丁。补丁只修改源码工作区，不替用户提交。发现不相关
改动或版本不匹配就停下来说明情况，不强行套用。

应用后重新用 `init --harness opencode` 初始化目标项目，并确认
`loop.harness = "opencode"`、`multilane.enabled = false`。不要在补丁里
预设 provider、模型或 API 凭据。

## 5. 最后带用户把 Archon 跑起来

阅读
[Archon 功能与使用引导](references/usage-zh.md)。

先问用户现在想做什么，再只介绍相关功能：

- 新建或接入项目：`init`
- 整理数学依赖：`dag`
- 自动形式化：`loop`
- 接着中断任务：`loop --resume`
- 讨论阻塞：`discuss`
- 查看进度：`dashboard`
- 拆分、合并或重构：`extract`、`merge`、`refactor`
- 多项目协作：`peers`、`scope`

原版 Claude Code 流程使用上游命令；OpenCode 流程显式选择
`--harness opencode` 或使用项目里已经保存的 OpenCode harness。说明这条命令
会做什么、会改哪些文件、用户应该看什么结果，然后陪用户跑完第一条有用的命令。

## 做事方式

- 用自然语言汇报检测结果，一次只问一个真正需要用户决定的问题。
- 不对用户说“授权门”“不变量”“阶段完成标准”等内部流程词。
- 保留用户的源码和 Git 改动；不擅自暂存、重置、提交或覆盖。
- OpenCode 流程不运行 `archon setup`，因为 v0.3.3 会安装 Claude Code。
- 补丁版不运行 `archon update`，也不启用 multilane。
- 未经用户同意，不运行会调用真实模型的测试。
