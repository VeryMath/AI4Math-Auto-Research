# 使用 Rethlas 解答自然语言数学题

Rethlas 读取 Markdown 数学题，生成非形式化证明蓝图，并由独立验证代理检查逻辑、
引用和证明缺口。生成代理根据验证反馈进行多轮修订。

## 1. 从任意对话定位 Rethlas

每次使用前运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor --json
```

将输出中的 `repository` 设为 `TARGET`。登记路径有效时，直接进入解题流程。
OpenCode 在新项目中请求外部目录权限时，向用户展示该路径并请求访问。

## 2. 准备题目

将题目保存到：

```text
$TARGET/agents/generation/data/<problem_id>.md
```

用户直接在对话中给出题目时，为它选择清晰的 `problem_id`，并将完整原题写入
Markdown 文件。例子：

```markdown
# Problem

Prove that every finite tree with at least two vertices has at least two leaves.
```

题目参考资料放入同名目录：

```text
data/<problem_id>.refs/
```

参考资料支持 Markdown、TeX、纯文本和 PDF。PDF 文本提取使用 `pdftotext`。

## 3. 启动 OpenCode 验证服务

在 OpenCode Desktop 的工作区终端中进入验证目录：

```bash
cd "$TARGET/agents/verification"
source .venv/bin/activate
uvicorn api.server_opencode:app --host 127.0.0.1 --port 8091
```

用户指定验证模型时：

```bash
OPENCODE_VERIFICATION_MODEL="provider/model" \
  uvicorn api.server_opencode:app --host 127.0.0.1 --port 8091
```

确认 `http://127.0.0.1:8091/health` 返回正常状态，然后保持该终端会话运行。

## 4. 运行证明生成

在另一个工作区终端中运行：

```bash
cd "$TARGET/agents/generation"
source .venv/bin/activate
PROBLEM_FILE="data/<problem_id>.md" ./tests/run_example_opencode.sh
```

用户指定生成模型或迭代次数时：

```bash
OPENCODE_GENERATION_MODEL="provider/model" \
MAX_ITERATIONS=10 \
PROBLEM_FILE="data/<problem_id>.md" \
  ./tests/run_example_opencode.sh
```

启动脚本在一次运行中维持同一个 OpenCode session，交替执行独立推理和资料检索，
并根据验证报告修复证明。真实模型调用前向用户说明 provider/model 和额度消耗。

## 5. 查看过程与结果

设题目相对路径为 `<problem_id>`，对应文件位于：

```text
$TARGET/agents/generation/memory/opencode/<problem_id>/
$TARGET/agents/generation/logs/opencode/<problem_id>/iter/
$TARGET/agents/generation/results/opencode/<problem_id>/blueprint.md
$TARGET/agents/generation/results/opencode/<problem_id>/blueprint_verified.md
```

`blueprint.md` 保存当前证明蓝图。验证通过后，最终结果写入
`blueprint_verified.md`。汇报时包含题目路径、模型、迭代次数、验证结论、结果路径
和日志路径。

安装 Zola 后，可在生成目录运行：

```bash
./site/serve.sh
```

结果网站地址为 `http://localhost:3264`。

## 6. OpenCode Desktop 对话示例

用户可以在任意项目的新对话中输入：

> 用 Rethlas 证明：每棵至少有两个顶点的有限树都至少有两个叶子。请持续汇报
> 生成、验证和修复过程，并给出最终证明蓝图与文件路径。

Skill 应自动读取已登记的 `rethlas_home`，创建题目文件，启动验证服务和生成流程，
并在当前对话中跟踪结果。

## 7. 常见检查项

- 已登记路径移动或失效；
- 新项目尚待确认 `external_directory` 权限；
- 8091 端口占用；
- OpenCode provider 登录状态；
- `PROBLEM_FILE` 路径；
- 生成侧与验证侧 MCP 状态；
- 达到迭代上限后的证明缺口。
