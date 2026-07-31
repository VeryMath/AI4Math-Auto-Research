# Rethlas 功能介绍与使用引导

使用本文件介绍 Rethlas 的能力，并引导用户完成一次有实际意义的运行。命令要
与用户选择的运行方式一致。

## 目录

1. 功能地图
2. 启动验证服务
3. 运行证明生成
4. 添加自定义题目
5. 提供私有参考资料
6. 查看输出与日志
7. 浏览结果网站
8. 引导与排错方法

## 1. 功能地图

Rethlas 是一套自然语言数学推理系统，包含两个主要代理：

- **生成代理：** 读取 Markdown 数学题，编写非形式化证明 blueprint。
- **验证代理：** 检查 blueprint，通过本地 HTTP API 返回结构化判定。

生成启动脚本会在多轮迭代中保持同一个模型 session，交替执行关闭检索和开启
检索的轮次，依据 verifier 反馈修复证明，并在得到已验证 blueprint 或达到
迭代上限时停止。

配套功能包括：

- 针对每道题提供 Markdown、TeX、文本或 PDF 参考资料；
- 保存可复用的 memory artifacts；
- 保存逐轮日志；
- 分开保存草稿和已验证结果；
- 使用 Zola 网站浏览带 LaTeX 公式的 Markdown 结果；
- 在原有 Codex 旁边选择性加入 OpenCode 运行方式。

只介绍与用户目标有关的功能，随后给出下一条具体命令。

## 2. 启动验证服务

生成前必须先启动验证服务。在 `agents/verification` 中激活对应环境。

原有 Codex 验证服务：

```bash
source .venv/bin/activate
uvicorn api.server:app --host 127.0.0.1 --port 8091
```

安装补丁后可用的 OpenCode 验证服务：

```bash
source .venv/bin/activate
uvicorn api.server_opencode:app --host 127.0.0.1 --port 8091
```

两者都使用 8091 端口，只运行与生成侧匹配的服务。保持该终端运行，先处理
启动错误，再进入生成步骤。

## 3. 运行证明生成

打开另一个终端，进入 `agents/generation` 并激活环境。

原有 Codex 工作流：

```bash
source .venv/bin/activate
./tests/run_example.sh
```

OpenCode 工作流：

```bash
source .venv/bin/activate
./tests/run_example_opencode.sh
```

运行 OpenCode 前，确认用户自己的 provider/API 已连接，并且已经选择模型：

```bash
opencode auth list
opencode models
```

补丁不提供默认模型。不设置模型环境变量时，使用用户自己的 OpenCode 配置。
需要固定生成和验证模型时，使用用户选定的模型标识：

```bash
OPENCODE_GENERATION_MODEL="provider/model" \
  ./tests/run_example_opencode.sh
```

```bash
OPENCODE_VERIFICATION_MODEL="provider/model" \
  uvicorn api.server_opencode:app --host 127.0.0.1 --port 8091
```

需要限制修复轮数时：

```bash
MAX_ITERATIONS=10 ./tests/run_example.sh
```

OpenCode 运行时使用相应的 OpenCode 脚本。首次模型调用前先征得用户同意，
并说明会消耗哪个 provider/model 的额度。

## 4. 添加自定义题目

将题目保存为 `agents/generation/data/` 下的 Markdown 文件，例如：

```text
agents/generation/data/my_problem.md
```

使用 Codex 运行：

```bash
PROBLEM_FILE=data/my_problem.md ./tests/run_example.sh
```

使用 OpenCode 运行：

```bash
PROBLEM_FILE=data/my_problem.md ./tests/run_example_opencode.sh
```

支持子目录：

```bash
PROBLEM_FILE=data/modrep/modrep.md ./tests/run_example.sh
```

生成产物会保留题目的相对目录结构。

## 5. 提供私有参考资料

创建与题目同名 stem 的相邻目录：

```text
data/modrep/modrep.md
data/modrep/modrep.refs/
```

生成代理会先读取这些参考资料，再使用外部检索。优先使用 Markdown、TeX 或
纯文本。PDF 支持需要 `pdftotext`，提取后的 PDF 文本写入 `.extracted/`。

除非用户明确希望纳入版本控制，否则不要将未公开或敏感参考资料加入 Git。

## 6. 查看输出与日志

原版 example 对应的路径为：

```text
memory/example/
logs/example/iter/
results/example/blueprint.md
results/example/blueprint_verified.md
```

`blueprint.md` 保存当前草稿。验证成功后会出现
`blueprint_verified.md`。没有生成已验证文件时，先检查逐轮日志和 verifier
终端，再判断失败原因。

OpenCode 的 example 产物隔离在：

```text
memory/opencode/example/
logs/opencode/example/
results/opencode/example/
```

这样 Codex 和 OpenCode 的运行结果不会互相覆盖。

## 7. 浏览结果网站

安装 Zola 后，在 `agents/generation` 中运行：

```bash
./site/serve.sh
```

首次运行会下载 MATbook 主题，需要网络访问。网站在
`http://localhost:3264` 本地提供服务，并按题目目录结构组织结果。

## 8. 引导与排错方法

进行使用引导时：

1. 说明当前功能和预期结果。
2. 确认工作目录与已激活的 `.venv`。
3. 启动匹配的 verifier，确认 8091 端口正在监听。
4. 展示或执行一条生成命令。
5. 指出准确的结果和日志路径。
6. 解释失败现象，并提出最小的下一项检查。

常见检查项：

- 8091 端口冲突或验证运行方式不匹配；
- provider 尚未登录；
- `PROBLEM_FILE` 路径错误；
- 缺少 PDF 提取工具；
- 生成和验证 MCP 连接状态；
- 达到迭代上限后仍未通过验证；
- 尚未选择用户自己的 OpenCode provider 或模型；
- 所选 provider 不提供指定 model 或 variant。

报告运行方式、模型、题目路径、结果路径、日志路径和最终验证状态。
