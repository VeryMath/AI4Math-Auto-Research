# 管理 OpenCode 兼容补丁

仅在用户明确选择 OpenCode 支持后读取本文件。用户要求检查、更新或移除已有
补丁时也读取本文件。

## 目录

1. 补丁包含的内容
2. 安装前检查
3. 安装
4. 验证
5. 移除
6. 报告

## 补丁包含的内容

随附补丁是基于上游 commit
`974b82ccfbcb07c405a233886e6e8d1d4db84828` 的标准 Git 补丁，共新增九个
OpenCode 专用文件：

- 英文和简体中文 OpenCode 使用说明；
- 生成侧和验证侧 `opencode.json`；
- OpenCode 专用 `AGENTS` 指令；
- OpenCode 生成启动脚本；
- OpenCode 验证 API；
- OpenCode 递归证明 skill。

补丁不编辑原有 Codex 文件。安装后仍可继续使用 Codex 命令。
补丁也不附带 provider、模型、variant、API key 或其他凭据；OpenCode 使用
用户自己的配置。

## 安装前检查

运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-status "$TARGET"
git -C "$TARGET" status --short
git -C "$TARGET" branch --show-current
git -C "$TARGET" rev-parse HEAD
```

保留无关修改。只在用户同意的非默认分支上安装；需要时创建或切换分支。除非
用户另外提出要求，否则不要暂存或提交。

遇到以下情况时停止：

- manifest 中的某个路径已经存在无关内容；
- 仓库处于补丁部分安装状态；
- `git apply --check` 失败；
- 尚未确定使用哪个分支。

## 安装

使用幂等 helper：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-apply "$TARGET"
```

helper 会在写入前校验打包文件 checksum 和适用性。较新的上游版本只有通过
适用性检查后才可安装。

用于直接检查的两个资源为：

```text
assets/rethlas-opencode-compat.patch
assets/rethlas-opencode-compat.json
```

不要使用 `--reject`，不要覆盖冲突，也不要只手动复制 manifest 的一部分。

## 验证

再次运行状态命令，确认输出 `patch_state: installed`。随后检查：

```bash
python3 -m json.tool "$TARGET/agents/generation/opencode.json"
python3 -m json.tool "$TARGET/agents/verification/opencode.json"
bash -n "$TARGET/agents/generation/tests/run_example_opencode.sh"
```

OpenCode 配置完成后，在相应目录中检查 agents 和 MCP 服务：

```bash
opencode agent list
opencode mcp list
```

确认原有 tracked 文件没有 diff。安装后的说明文件为：

- `README.opencode.md`
- `README.opencode.zh-CN.md`

首次运行前，引导用户检查 `opencode auth list`，通过 `/connect` 连接服务，
并用 `opencode models` 查看模型。coding plan 或 API provider 以及模型均由
用户选择。不要在项目文件或启动脚本中加入 fallback 模型。

调用任何模型进行冒烟测试前先征得用户同意。

## 移除

只有九个文件仍全部匹配补丁时，才能安全移除：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-remove "$TARGET"
```

helper 会执行 reverse applicability check，并拒绝删除已修改文件。报告冲突，
不要强行移除。

## 报告

报告补丁状态、分支、`HEAD`、checksum 结果、冲突、验证结果，以及用户后续
准备使用 Codex、OpenCode 或两者。
