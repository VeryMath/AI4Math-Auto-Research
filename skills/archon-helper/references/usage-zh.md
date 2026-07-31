# Archon 功能与使用引导

## 目录

1. 使用前约定
2. 项目创建与健康检查
3. Blueprint 与自动形式化
4. 交互、监控和恢复
5. 项目拆分、合并和重构
6. 多项目协作
7. 版本、迁移和维护
8. Subagent、状态和保护
9. 推荐引导方式

## 1. 使用前约定

统一使用当前 `<archon-dir>/.venv/bin/archon`，避免调用系统里的另一版本。

- 选择原版 Claude Code：命令中省略 `--harness opencode`，使用 Archon 默认
  harness。
- 选择 OpenCode：带 agent 的交互命令支持 `--harness` 时显式传
  `--harness opencode`，其余命令从项目配置继承。

OpenCode 项目先确认：

```text
.archon/config.json: loop.harness = opencode
.archon/config.json: multilane.enabled = false
.opencode/skills/lean4/SKILL.md 存在
.opencode/tools/archon-subagent.py 存在
```

## 2. 项目创建与健康检查

### `archon init`

作用：初始化空目录、已有 Lean/Lake 项目，或含 Markdown、LaTeX、PDF 等材料的
目录；创建 `.archon/`、Lean 骨架和所选运行器的项目工具。

```bash
<archon-bin> init <project>
<archon-bin> init <project> --harness opencode
```

第一条用于原版 Claude Code，第二条用于 OpenCode。

无人值守时可加 `--headless`。已有 `.archon/` 时先查看配置和差异；`--force`
会覆盖 Archon 管理文件，必须取得用户确认。

### `archon doctor`

作用：检查系统工具、包数据、项目状态、所选运行器的项目文件、Lean-LSP 和认证。

```bash
<archon-bin> doctor <project> --skip-auth
<archon-bin> doctor <project>
```

第一条不调用 provider。第二条会发出真实请求，只在用户许可后运行。

### `archon version`

作用：显示 CLI 版本；在项目内同时显示 init 写入的项目版本。

```bash
<archon-bin> version <project>
```

## 3. Blueprint 与自动形式化

### `archon dag`

作用：让 agent 编写完整 informal blueprint，以 `\uses{}` 标注依赖，并建立
LeanDAG。复杂项目建议在 loop 前运行。

```bash
<archon-bin> dag <project> --max-iterations 4
```

它从项目配置继承已经选定的运行器，会产生 provider 请求。

### `archon blueprint-doctor`

作用：静态检查 blueprint 的断链、孤立章节、引用、宏、axiom 和覆盖标记。

```bash
<archon-bin> blueprint-doctor <project>
```

该命令适合在 dag 后和提交前运行，不需要模型判断。

### `archon loop`

作用：运行核心 `plan → prover → review` 循环，并把每个阶段提交到项目的 inner
Git。默认后台启动 Dashboard。

```bash
<archon-bin> loop <project>
<archon-bin> loop <project> --max-iterations 3
<archon-bin> loop <project> --serial
<archon-bin> loop <project> --focus "优先处理 Foo.lean 中的 theorem bar"
<archon-bin> loop <project> --no-dashboard
<archon-bin> loop <project> --no-review
```

普通并行 prover 可用，`--max-parallel` 控制并发。不要启用 multilane。

### `archon prove`

作用：为一条文本命题创建临时工作区并自动执行 init 与 loop。

原版 Claude Code 流程可以直接使用：

```bash
<archon-bin> prove '<statement>' <project>
```

0.3.3 的该快捷命令没有把 harness 传给内部 init，因此 OpenCode 流程采用等价
的显式步骤：

```bash
mkdir -p <project>
<archon-bin> init <project> --harness opencode
<archon-bin> loop <project>
```

在 init 前使用文件编辑工具创建 `<project>/statement.md`，内容为待证明命题。

## 4. 交互、监控和恢复

### `archon discuss`

作用：打开带完整项目上下文的交互会话，讨论证明阻塞、Mathlib 引理和策略，并可
把结论写入 `USER_HINTS.md`。

```bash
<archon-bin> discuss <project>
<archon-bin> discuss <project> --harness opencode
<archon-bin> discuss <project> --harness opencode --focus "theorem bar"
```

### `archon dashboard`

作用：查看阶段进度、并行 prover、日志、diff、DAG、blueprint 和 proof journal。

```bash
<archon-bin> dashboard <project> --open
<archon-bin> dashboard <project> --port 8080
```

Dashboard 需要 Node.js。loop 已默认启动时，优先使用终端打印的 URL。

### `archon loop --resume`

作用：从中断迭代的最后完成阶段继续。

```bash
<archon-bin> loop <project> --resume
<archon-bin> loop <project> --resume --from prover
```

`--from` 可取 `plan`、`prover`、`review`。找不到所选运行器的 session id 时会
启动新会话。

### `archon log` 与 `archon branch`

作用：查看 Archon inner Git 历史，或从历史提交创建替代策略分支。

```bash
<archon-bin> log <project> -n 30
<archon-bin> branch alt-strategy <project> --from <commit>
<archon-bin> branch main <project>
```

`branch --force` 可能覆盖 inner-tracked 改动，除非用户明确要求，否则不使用。

## 5. 项目拆分、合并和重构

### `archon extract`

作用：按 blueprint DAG 的依赖闭包从父项目提取子项目。父项目保持只读，默认在
新目录创建 sandbox。

```bash
<archon-bin> extract <parent> \
  --dest <new-project> \
  --harness opencode \
  --build
```

目标目录必须不存在。中断或验证失败后用 `--resume` 继续。

### `archon merge`

作用：经 DAG 合并两个 Archon 项目，处理共享声明的证明选择和语句冲突。

```bash
<archon-bin> merge <target> \
  --from <source> \
  --dest <merged-project> \
  --harness opencode
```

默认创建 sandbox 并执行 `lake build`。`--in-place` 会直接修改 target；使用前
必须让用户确认，并先查看项目状态。`--union` 会引入 source 的非共享依赖锥。

### `archon refactor`

作用：先通过访谈生成重构指令，再让 refactor agent 执行并提交到 inner Git。

```bash
<archon-bin> refactor draft <project> --harness opencode
<archon-bin> refactor run <project>
```

先审阅 `.archon/REFACTOR_DIRECTIVE.md`，再执行 run。不要默认使用
`draft --auto-run`。

## 6. 多项目协作

### `archon peers`

作用：读取 `peers.yaml` 指定的同类项目，查看复用关系，并通过 inbox 提交代码
泛化建议或数学/架构问题。

```bash
<archon-bin> peers --project-path <project>
<archon-bin> peers inbox --project-path <project>
<archon-bin> peers pr --project-path <project> \
  --target <peer> --lean-name <Lean.Name> --code '<code>'
<archon-bin> peers issue --project-path <project> \
  --target <peer> --title '<title>' --body '<description>'
```

`pr` 和 `issue` 会写入 peer 的 `.archon/inbox/`，属于跨项目写操作；执行前向
用户确认目标和内容。使用 `accept` 或 `decline` 处理收到的条目。

### `archon scope`

作用：管理一组 Archon 项目，生成 union DAG、跨项目 roadmap 和统一 Dashboard。

```bash
<archon-bin> scope init <scope-dir>
cd <scope-dir>
<archon-bin> scope add '<project-path-or-glob>'
<archon-bin> scope ls
<archon-bin> scope graph
<archon-bin> scope roadmap --harness opencode
<archon-bin> scope discuss --harness opencode
<archon-bin> scope dashboard
```

先用 `scope ls` 核对成员，随后再运行图、roadmap 或交互功能。

## 7. 版本、迁移和维护

### `archon migrate`

作用：执行旧项目的一次性结构迁移。0.3.3 当前提供 session 目录重命名：

```bash
<archon-bin> migrate rename-sessions <project>
```

迁移前查看 Git 状态，并运行子命令的 `--help` 确认影响。

### `archon setup`

作用：上游用于安装系统依赖和 Claude Code。选择原版时可以在用户确认后使用；
OpenCode 流程不调用它，按 `environment-zh.md` 分别配置依赖。

### `archon update`

作用：把原版 Archon 更新到上游最新版本。OpenCode 补丁只验证了固定 0.3.3
基线，补丁版不调用 update。需要升级时另建检出，重新审计和生成补丁。

## 8. Subagent、状态和保护

subagent 默认关闭。在 `.archon/config.json` 中启用：

```json
{
  "subagents": {
    "enabled": [
      "strategy-critic",
      "blueprint-reviewer",
      "lean-auditor"
    ]
  }
}
```

也可设为 `"*"`。原版 subagent 继承 Claude Code；OpenCode 模式不要把单个
subagent 覆盖回 `claude-code`，它们由 `.opencode/tools/archon-subagent.py`
调度。

主要状态：

- `.archon/PROGRESS.md`：当前阶段和进度；
- `.archon/USER_HINTS.md`：用户长期提示；
- `.archon/TO_USER.md`：Archon 给用户的问题；
- `.archon/logs/`：agent 与迭代日志；
- `.archon/iter/`：每轮 plan/review 记录；
- `.archon/proof-journal/`：证明经验。

临时提示使用 `loop --focus`，长期提示编辑 `USER_HINTS.md`。需要保护声明或文件时
查看并配置项目根目录的 `archon-protected.yaml`。

## 9. 推荐引导方式

根据目标只给一条主路径：

- 从零开始：`init → doctor → dag（可选）→ loop → dashboard`；
- 继续中断任务：`doctor → loop --resume`；
- 理解阻塞：`discuss → USER_HINTS.md → loop --focus`；
- 拆分项目：`blueprint-doctor → extract --build`；
- 合并成果：`merge` 到新 sandbox，验证后再替换正式目录；
- 大规模结构调整：`refactor draft → 人工审阅 → refactor run`；
- 多项目协调：`scope init/add/ls → graph/roadmap/dashboard`。

每一步说明预期输出、会写入的目录、是否调用模型，以及失败后的恢复命令。
