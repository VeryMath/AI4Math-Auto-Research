# 配置 Archon 的 OpenCode 与 Lean 环境

本阶段检查 Archon CLI、Lean 工具链、OpenCode provider 和当前项目配置。

## 1. 解析 Archon 安装与当前项目

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" doctor "$PROJECT" --json
```

从输出取得 `ARCHON_HOME`、`ARCHON_BIN`、补丁状态和项目状态。CLI 文件位于：

```text
$ARCHON_HOME/.venv/bin/archon
```

后续命令统一使用该绝对路径。

## 2. 检查基础工具

```bash
python3 --version
git --version
elan --version
lean --version
lake --version
uv --version
opencode --version
```

各组件用途：

- Python 3.10+：运行 Archon CLI；
- Git：管理 Archon 源码和项目历史；
- Elan、Lean、Lake：构建形式化项目；
- uv：启动 Lean-LSP MCP；
- OpenCode：运行 Archon agent 与 subagent。

软件安装方式可能随平台变化。检查当前操作系统和官方安装说明，并在联网安装前
征得用户同意。

## 3. 检查 OpenCode provider 与模型

```bash
opencode auth list
opencode models
```

provider 连接在 OpenCode 中通过 `/connect` 或相应登录界面完成。用户选择自己的
provider、模型和 variant。登录信息保存在 OpenCode 用户配置中。

需要为 Archon 项目指定模型时，在 `.archon/config.json` 的
`harnesses.opencode` 中设置完整的 `provider/model` 标识。修改前读取现有配置，
并维护其他项目字段。

## 4. 检查可选工具

根据任务检查：

```bash
node --version
npm --version
rg --version
pdftotext -v
leanblueprint --help
```

- Node.js/npm：Archon Dashboard；
- ripgrep：源码检索；
- Poppler：PDF 材料提取；
- LeanBlueprint：数学 blueprint 的生成与渲染。

## 5. 初始化当前项目

项目尚未初始化时运行：

```bash
"$ARCHON_BIN" init "$PROJECT" --harness opencode
```

已有 `.archon/config.json` 时，先检查 doctor 输出。项目需要补齐 OpenCode 文件时，
向用户说明 re-init 会更新的 Archon 管理文件，再运行相同命令。

OpenCode 项目的关键状态为：

```text
.archon/config.json: loop.harness = opencode
.archon/config.json: multilane.enabled = false
.opencode/skills/lean4/SKILL.md
.opencode/tools/archon-subagent.py
```

## 6. 检查项目

运行 Archon 项目检查：

```bash
"$ARCHON_BIN" doctor "$PROJECT" --skip-auth
```

随后检查 Lean 项目：

```bash
cd "$PROJECT"
lake build
```

用户批准真实 provider 请求后，可运行：

```bash
"$ARCHON_BIN" doctor "$PROJECT"
```

汇报 CLI 版本、Lean 工具链、OpenCode provider、项目 harness、Lean-LSP 状态和
构建结果。真实模型调用前说明 provider/model 与额度消耗。
