# 安装或克隆 Rethlas

本文件只处理仓库定位与获取。Python 环境、provider 登录、OpenCode 补丁和
首次运行命令分别留到对应阶段。

## 1. 确定路径

将 `SKILL_DIR` 设为包含主 `SKILL.md` 的目录，将 `TARGET` 设为目标
Rethlas 仓库根目录。

用户没有提供 `TARGET` 时，先搜索当前工作区。有效仓库根目录必须包含：

- `agents/generation/AGENTS.md`
- `agents/generation/.codex/config.toml`
- `agents/verification/AGENTS.md`
- `agents/verification/.codex/config.toml`

## 2. 检查已有仓库

运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor "$TARGET"
```

同时检查：

```bash
git -C "$TARGET" status --short
git -C "$TARGET" branch --show-current
git -C "$TARGET" rev-parse HEAD
git -C "$TARGET" remote -v
```

保留全部无关的 tracked 和 untracked 文件。目录不符合 Rethlas 结构时，先
报告缺少哪些必要路径，再提议克隆到其他位置。

## 3. 尚未安装时进行克隆

优先使用用户指定的仓库；用户未指定时使用官方上游：

```bash
git clone https://github.com/frenzymath/Rethlas.git "$TARGET"
```

克隆需要网络访问，执行前先征得用户同意。不要覆盖非空目标目录。

克隆后记录：

- 仓库绝对路径；
- origin URL；
- 当前分支和 `HEAD`；
- doctor 是否识别该仓库。

## 阶段边界

仓库已经存在且结构有效后，安装阶段即告完成。随后进入环境阶段，处理 CLI、
Python 环境、登录和运行时检查。本阶段不要安装 OpenCode 补丁。
