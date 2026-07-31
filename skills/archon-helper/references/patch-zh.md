# 补丁确认、应用与验证

## 目录

1. 先确认用户选择
2. 应用前检查
3. 只检查
4. 应用
5. 项目迁移
6. 补丁行为
7. 限制
8. 验证

## 1. 先确认用户选择

只在用户已经选择 OpenCode 后进入本流程。运行器选择和自然语言问法见
`SKILL.md`；不要到了这里又问一遍。

用户只想看看兼容性时运行 `--check-only`。用户选择安装时继续应用流程。用户想
保留原版时保持源码不变，回到 Claude Code 环境配置。

## 2. 应用前检查

确认：

```bash
git -C <archon-dir> status --short
git -C <archon-dir> rev-parse HEAD
```

要求：

- `pyproject.toml` 项目名为 `archon`；
- 版本为 0.3.3；
- 首选基线提交为 `5e9ae7615efa0aa2cff11edabd5fbc0d45308fd5`；
- 工作区无用户改动；
- 随附补丁文件存在。

发现用户改动时停止。让用户自行提交、stash，或另建干净 clone。不要执行
`git reset --hard`、`git checkout --` 或其他丢弃操作。

## 3. 只检查

```bash
python3 <skill-dir>/scripts/apply_patch.py \
  --repo <archon-dir> \
  --check-only
```

报告补丁是否可干净应用。检查失败时保留原始错误，不使用 `--reject` 制造半应用
工作区，也不手工模糊匹配到未知版本。

## 4. 应用

得到授权并通过检查后：

```bash
python3 <skill-dir>/scripts/apply_patch.py \
  --repo <archon-dir>
```

脚本会：

- 验证 Archon 版本和 Git 状态；
- 运行 `git apply --check`；
- 应用 `assets/patches/archon-v0.3.3-opencode.patch`；
- 编译检查 `src/archon`；
- 检查 OpenCode CLI 是否可见。

脚本不提交改动。应用后展示：

```bash
git -C <archon-dir> status --short
git -C <archon-dir> diff --stat
```

## 5. 项目迁移

新项目：

```bash
<archon-bin> init <project> --harness opencode
```

已有 `.archon/` 的项目也要重新执行带 harness 的 init，才能生成：

```text
<project>/.opencode/skills/lean4/SKILL.md
<project>/.opencode/tools/archon-subagent.py
```

仅编辑 `loop.harness` 不会安装这些项目文件。已有项目先保留配置并交互式处理
re-init；只有用户确认后才传 `--force`。

## 6. 补丁行为

当 `loop.harness = "opencode"` 时：

- init 语义阶段、plan、prover、review、resume 和 Archon subagent 使用 OpenCode；
- 通用 harness router 供 dag、discuss、extract、merge、refactor 等 agent 命令使用；
- Lean 指令和 subagent wrapper 安装到 `.opencode/`；
- 运行时注入 Lean-LSP MCP；
- 禁用 OpenCode 的 Claude Code 兼容导入；
- 跳过 Claude 认证、插件、MCP 和 session store 检查。

## 7. 限制

- multilane 的 lane runner 与 merge agent 仍依赖 Claude。OpenCode 模式会
  fail-closed 并关闭 multilane；普通串行和并行 prover 可用。
- `archon setup` 会安装 Claude Code；OpenCode 安装流程不使用它。
- `archon update` 会改变源码基线；补丁版不使用它。
- `archon prove` 在原版 0.3.3 内部调用未指定 harness 的 init。OpenCode 流程
  使用显式 `init --harness opencode` 再运行 `loop`。
- CLI 帮助和源码兼容路径中仍可能保留 Claude 文案。以配置、doctor 和日志里的
  `runner: opencode` 判断实际运行器。

## 8. 验证

无额度验证：

```bash
<archon-bin> doctor <project> --skip-auth
cd <project>
lake build
```

真实 provider 验证只在用户许可后运行：

```bash
<archon-bin> doctor <project>
```

检查日志中的 session 起始记录包含：

```json
{"runner": "opencode"}
```

若 `src/archon/agents/opencode.py` 已存在，脚本会避免重复应用。不要据此跳过项目
配置和 doctor。
