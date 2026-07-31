# 配置 Rethlas 环境

按照以下检查表逐项引导用户，避免一次抛出没有层次的命令集合。先说明每个组件
对应的功能，再检查已有状态，只安装所选工作流真正需要的内容。

## 目录

1. 确认运行方式
2. 检查基础工具
3. 创建两个 Python 环境
4. 选择 Codex 时进行配置
5. 选择 OpenCode 时进行配置
6. 在不调用模型的情况下验证
7. 遵守阶段边界

## 1. 确认运行方式

上游 Rethlas 基于 Codex。先检查 Codex CLI 是否可用：

```bash
command -v codex
codex --version
```

按照主 `SKILL.md` 中的条件分流：

- 没有 Codex 时，说明原版依赖关系，并询问是否安装 OpenCode 补丁；
- 已有 Codex 时，询问直接使用原版，还是加入 OpenCode 运行方式；
- 补丁已经安装时，询问本次要配置哪一种现有运行方式。

不要仅因缺少 Codex 就替用户选择 OpenCode，也不要替用户决定 provider 或
模型。

先运行诊断：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor "$TARGET"
```

提出修改建议前，先概括已经具备的环境。

## 2. 检查基础工具

检查：

```bash
git --version
python3 --version
uv --version
```

优先使用已安装的 Python 3.12 或 3.13。有 `uv` 时使用 `uv`，否则使用
`python3 -m venv` 和 `pip`。

可选工具：

- Poppler 提供的 `pdftotext`，用于提取 PDF 参考资料；
- Zola，用于本地结果网站；
- Node/npm，仅在安装 Codex 时按需使用。

提议安装可选组件前，先说明它所支持的功能。联网安装前征得用户同意。

## 3. 创建两个 Python 环境

Rethlas 将证明生成和证明验证分开运行。即使两侧使用同一个 Python，也要创建
两个独立环境：

```bash
uv venv "$TARGET/agents/generation/.venv" --python 3.13
uv pip install \
  --python "$TARGET/agents/generation/.venv/bin/python" \
  -r "$TARGET/agents/generation/mcp/requirements.txt"

uv venv "$TARGET/agents/verification/.venv" --python 3.13
uv pip install \
  --python "$TARGET/agents/verification/.venv/bin/python" \
  -r "$TARGET/agents/verification/requirements.txt"
```

没有 `uv` 时，分别创建并激活 `.venv`，再用 `pip` 安装对应 requirements
文件。环境保留在项目现有的 ignored 运行目录中。

使用每个环境自己的 Python 检查 imports 或包信息。仅看到目录存在还不足以
判定环境就绪。

## 4. 选择 Codex 时进行配置

分别检查 CLI 和用户级登录状态：

```bash
codex --version
codex login status
```

CLI 缺失时，安装前检查当前上游和官方说明。已检出的 Rethlas README 可能
记录以下命令：

```bash
npm install -g @openai/codex
```

不要通过编辑项目 `.codex` 文件修复用户级 wrapper。定位可用的 executable，
或修复用户环境。凭据保留在仓库之外。

## 5. 选择 OpenCode 时进行配置

检查：

```bash
opencode --version
opencode auth list
opencode models
```

需要登录时，引导用户在 OpenCode TUI 中使用 `/connect`。由用户选择可用的
coding plan 或 API provider，完成连接后，再从 `opencode models` 显示的
列表中选择模型。不要索取凭据内容，也不要将 OpenCode 凭据存储复制到
Rethlas。

随附补丁不设置默认 provider、模型、variant 或 API key。没有单次运行覆盖
时，OpenCode 使用用户自己的配置。可选的
`OPENCODE_GENERATION_MODEL` 和 `OPENCODE_VERIFICATION_MODEL` 必须来自
用户选择的 `provider/model`。

## 6. 在不调用模型的情况下验证

确认：

- 两个 Python 环境使用预期解释器；
- 生成侧 MCP 依赖可以正常 import；
- 验证 API 依赖可以正常 import；
- 所选 CLI executable 可以正确解析；
- 已知登录状态，同时不暴露 secret；
- Poppler 和 Zola 状态符合用户计划使用的功能。

将各项标记为已就绪、缺失、可选或等待用户操作。进入 provider 登录流程或
付费模型冒烟测试前先征得用户同意。

## 阶段边界

环境验证完成后返回主 `SKILL.md`。用户已选择 OpenCode 且补丁尚未安装时，
进入补丁阶段；用户选择原版 Codex 时，直接进入使用引导。
