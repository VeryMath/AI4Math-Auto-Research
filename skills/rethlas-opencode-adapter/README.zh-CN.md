# Rethlas OpenCode Adapter

[English](README.md) | 简体中文

`rethlas-opencode-adapter` 帮助 coding agent 克隆 FrenzyMath Rethlas、应用 OpenCode 适配补丁，并通过用户已有的 OpenCode 安装运行 Rethlas 标准 generation/verification 流程。

## 适合什么任务

当用户有这些需求时使用：

- 在已经安装 OpenCode 的电脑上部署 Rethlas；
- 用 OpenCode 运行 Rethlas 证明生成流程；
- 让 coding agent 给干净 Rethlas clone 打补丁，然后监督标准 `tests/run_example.sh` 流程。

## 会产出什么

适配后得到一个带有这些内容的 Rethlas clone：

- 支持 OpenCode 的 generation runner；
- 支持 OpenCode 的 verification service；
- generation 侧 `.opencode` agent 和 MCP 配置；
- verification 侧 `.opencode` agent 和 MCP 配置。

补丁不加入示例问题、生成证明、测试缓存或用户凭证。

## 安装

把下面这句话发给你的 coding agent：

```text
请帮我安装 `rethlas-opencode-adapter` skill，链接是：https://github.com/VeryMath/AI4Math-Auto-Research.git。请读取包内 `SKILL.md`，安装其中声明的 Skill entrypoint，验证 `$rethlas-opencode-adapter` 可用，并告诉我是否需要重启 agent。
```

如果你已经有这个 skill 仓库的本地文件夹，把链接换成本地路径即可。

## 快速开始

```text
Use $rethlas-opencode-adapter.

请把 FrenzyMath Rethlas 克隆到 ./external/Rethlas，应用 OpenCode 适配补丁，
把我的问题写入 agents/generation/data/，用 Python virtual environment 安装依赖，
用 OpenCode 启动 verification service，用 OpenCode 运行 generation runner，
并只监督外层进程直到 blueprint_verified.md 出现。
```

## 维护检查

修改后先检查 Skill 形状：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/rethlas-opencode-adapter
```

检查 adapter 脚本：

```bash
python3 -B skills/rethlas-opencode-adapter/scripts/apply_adapter.py --help >/dev/null
python3 - <<'PY'
from pathlib import Path
import ast
ast.parse(Path("skills/rethlas-opencode-adapter/scripts/apply_adapter.py").read_text())
PY
```

