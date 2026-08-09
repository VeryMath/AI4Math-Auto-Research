# 安装 OpenCode 兼容文件

本阶段将 Rethlas 的生成代理和验证代理接入 OpenCode。

## 1. 补丁内容

随附 Git 补丁为 Rethlas 增加：

- OpenCode 使用说明；
- 生成侧与验证侧 `opencode.json`；
- OpenCode 专用 `AGENTS` 指令；
- OpenCode 生成启动脚本；
- OpenCode 验证 API；
- OpenCode 递归证明 skill。

provider、模型、variant 和 API 凭据来自用户的 OpenCode 配置。

## 2. 检查适用性

`TARGET` 已由用户配置文件解析。运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-status
git -C "$TARGET" status --short
git -C "$TARGET" branch --show-current
git -C "$TARGET" rev-parse HEAD
```

向用户报告当前分支、工作区改动和 `patch_state`。补丁安装使用用户批准的功能
分支。仓库出现部分安装或冲突状态时，展示相关路径并等待用户处理意见。

## 3. 应用补丁

用户确认分支和仓库修改后运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-apply
```

helper 先执行 `git apply --check`，随后应用随附补丁。再次运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-status
```

预期状态为：

```text
patch_state: installed
```

## 4. 检查 OpenCode 入口

在对应目录中运行：

```bash
cd "$TARGET/agents/generation"
opencode agent list
opencode mcp list
```

```bash
cd "$TARGET/agents/verification"
opencode agent list
opencode mcp list
```

确认生成侧能够看到证明 agent 与 reasoning MCP，验证侧能够看到验证 agent 与
verification MCP。真实模型调用前说明 provider/model 和额度消耗，并征得用户
同意。

## 5. 恢复补丁前状态

用户明确要求恢复且补丁状态完整时运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-remove
```

helper 使用 reverse applicability check 检查当前文件，再执行反向应用。局部修改
造成冲突时，报告路径和 Git 输出。

## 6. 报告

报告以下信息：

- Rethlas 安装路径；
- 分支与 `HEAD`；
- 补丁状态；
- OpenCode agent 和 MCP 列表；
- 用户选择的 provider/model；
- 下一条真实解题命令。
