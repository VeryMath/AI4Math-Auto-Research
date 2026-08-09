# 配置 Rethlas 的 OpenCode 环境

本阶段准备 OpenCode CLI、两个 Python 环境和用户选定的 provider/model。

## 1. 解析已登记安装

运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor --json
```

将输出中的 `repository` 设为 `TARGET`。报告补丁状态、Python 环境状态以及
OpenCode 命令路径。

## 2. 检查基础工具

```bash
git --version
python3 --version
uv --version
opencode --version
```

Rethlas 环境建议使用 Python 3.12 或 3.13。`uv` 用于创建环境和安装依赖。

可选工具：

- Poppler 的 `pdftotext`：读取 PDF 参考资料；
- Zola：浏览本地证明结果网站。

联网安装任何组件前，说明用途并征得用户同意。

## 3. 创建生成与验证环境

Rethlas 的生成代理和验证代理分别使用独立环境：

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

系统使用其他受支持 Python 版本时，将 `--python` 改为已确认的解释器。检查
每个环境的 Python 路径和依赖导入结果。

## 4. 使用 OpenCode provider 和模型

检查用户级 OpenCode 配置：

```bash
opencode auth list
opencode models
```

需要连接 provider 时，在 OpenCode 中引导用户完成 `/connect`。provider、模型
和 variant 由用户选择。Rethlas 项目保存运行文件，OpenCode 用户目录保存登录
信息。

运行时可使用当前 OpenCode 默认模型，也可由用户提供明确模型标识：

```text
provider/model
```

对应的运行变量为：

```text
OPENCODE_GENERATION_MODEL
OPENCODE_VERIFICATION_MODEL
```

## 5. 检查环境状态

确认：

- `doctor` 从用户配置解析到正确的 `TARGET`；
- 两个 Python 环境使用预期解释器；
- 生成侧 MCP 依赖能够导入；
- 验证 API 依赖能够导入；
- OpenCode CLI 能读取用户的 provider 和模型列表；
- Poppler 与 Zola 的状态符合用户任务需求。

真实模型调用会消耗 provider 额度。第一次调用前说明使用的模型并征得用户同意。

完成后进入 OpenCode 兼容文件安装阶段。
