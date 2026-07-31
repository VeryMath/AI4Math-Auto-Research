# 环境配置流程

## 目录

1. 公共环境
2. 配置选定的运行器
3. 可选环境
4. Archon 项目配置
5. 验证与排错

## 1. 公共环境

先检测，随后逐项引导用户处理缺失项：

```bash
python3 --version
git --version
elan --version
lean --version
lake --version
uv --version
```

核心要求：

- Python 3.10+：运行 Archon CLI；
- Git：管理 Archon 源码和项目历史；
- Elan、Lean、Lake：构建 Lean 项目；
- uv：启动 Lean-LSP MCP。

缺少工具时先识别操作系统、包管理器和用户现有安装方式。优先采用对应项目的
当前官方安装说明；软件安装方式可能变化，不凭记忆给出未经核对的下载命令。
全局安装、修改 shell 启动文件或写入系统目录前说明影响。

## 2. 配置选定的运行器

只配置用户已经选择的运行器。

### 原版 Claude Code

检查：

```bash
command -v claude
claude --version
```

如果 Claude Code 不可用，回到 `SKILL.md` 的运行器选择，不要继续假设原版能够
运行。用户选择安装 Claude Code 时，使用当前官方安装说明，并引导用户在自己的
终端完成登录；不索取账号或凭据。

### OpenCode

检查 CLI 与已有登录：

```bash
opencode --version
opencode auth list
```

没有可用 provider 时：

```bash
opencode auth login
```

先问用户准备用自己的哪种订阅或 API provider，再带他们完成 OpenCode 的交互式
登录。不要默认选择 DeepSeek、OpenAI、Anthropic 或任何其他 provider，也不要
替用户默认指定模型。

需要固定模型时，让用户先查看自己的可用模型：

```bash
opencode models
```

确认完整的 `provider/model` ID 后再写配置。不要求用户把密钥发到对话中，不打印
认证文件，不把密钥写入 `.archon/config.json`。

## 3. 可选环境

按用户要使用的功能检查：

```bash
node --version
npm --version
rg --version
pdftotext -v
leanblueprint --help
```

- Node.js/npm：Dashboard 构建和运行；
- ripgrep：更快的源码检索；
- Poppler：读取 PDF 参考材料；
- LeanBlueprint：生成和渲染数学 blueprint。

可选工具缺失时只限制相关功能，不阻塞普通 `init`、`loop` 或 `lake build`。

真实请求会消耗 provider 额度。仅在用户明确同意后运行最小请求；平时用
所选运行器的登录状态和 Archon 的 `doctor --skip-auth` 做静态检查。

## 4. Archon 项目配置

选择原版 Claude Code 时，直接运行 `archon init <project>`，让项目沿用默认
`claude-code` harness。

选择 OpenCode 时，补丁应用并完成 `init --harness opencode` 后检查
`<project>/.archon/config.json`：

```json
{
  "loop": {
    "harness": "opencode",
    "parallel": true,
    "max_parallel": 4
  },
  "harnesses": {
    "opencode": {
      "runner": "opencode",
      "mcp": "lean-lsp",
      "prompt_variant": "opencode"
    }
  },
  "multilane": {
    "enabled": false
  }
}
```

这是相关字段示例，不要用它覆盖完整配置。需要固定模型时只在
`harnesses.opencode` 中增加：

```json
"model": "provider/model"
```

检查 `loop.roles.<role>` 与 `subagents.<name>.harness`，避免局部配置覆盖回
`claude-code`。

## 5. 验证与排错

项目初始化后先运行：

```bash
<archon-bin> doctor <project> --skip-auth
```

用户同意真实 provider 测试后运行：

```bash
<archon-bin> doctor <project>
```

再验证 Lean：

```bash
cd <project>
lake build
```

常见问题：

- 找不到 `archon`：固定使用 `<archon-dir>/.venv/bin/archon`。
- 原版找不到 `claude`：确认 Claude Code 已安装且当前 shell 可以访问；仍不可用
  时回到运行器选择。
- 找不到 `opencode`：检查运行 Archon 的 shell 是否拥有同一 `PATH`；必要时
  在 `harnesses.opencode.bin` 配置绝对路径。
- provider 请求失败：检查所选运行器的登录状态、网络、额度和模型权限。
- doctor 仍检查 Claude：确认 `loop.harness`、role override、subagent override
  均指向 OpenCode，并重新执行 `init --harness opencode`。
- Lean-LSP 不可用：检查 uv、项目 `.opencode/` 文件和 `lake build`。
