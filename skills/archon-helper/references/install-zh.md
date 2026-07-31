# 安装与 clone 流程

## 目标

取得一份可追踪、可打补丁的 Archon 源码，并把 CLI 安装到独立虚拟环境。

已测试基线：

```text
仓库：https://github.com/frenzymath/Archon.git
提交：5e9ae7615efa0aa2cff11edabd5fbc0d45308fd5
版本：0.3.3
```

## 1. 发现现状

依次检查：

```bash
command -v archon
archon version
rg --files -g pyproject.toml <search-root>
```

只把 `pyproject.toml` 中项目名为 `archon` 的目录视为 `<archon-dir>`。记录
现有 CLI 路径，防止后续调用到另一份全局安装。

## 2. clone 原版

用户没有源码时，先确认目标路径不存在，再执行：

```bash
git clone https://github.com/frenzymath/Archon.git <archon-dir>
git -C <archon-dir> checkout 5e9ae7615efa0aa2cff11edabd5fbc0d45308fd5
```

不要用浮动的 `main` 作为补丁基线。上游没有 `v0.3.3` tag；上述提交对应
`pyproject.toml` 版本 0.3.3。

已有 clone 时运行：

```bash
git -C <archon-dir> status --short
git -C <archon-dir> rev-parse HEAD
```

发现用户改动或不同提交时保留现场。补丁兼容性稍后由 `--check-only` 判断。

## 3. 创建隔离环境

确认 Python 版本至少为 3.10，然后：

```bash
python3 -m venv <archon-dir>/.venv
<archon-dir>/.venv/bin/python -m pip install -e <archon-dir>
<archon-dir>/.venv/bin/archon version
```

安装依赖可能访问网络；执行前告知用户。使用 editable 安装后，源码补丁会立即
反映到 CLI。若入口或依赖定义发生变化，再运行一次 `pip install -e`。

后续把以下绝对路径记为 `<archon-bin>`：

```text
<archon-dir>/.venv/bin/archon
```

## 4. 安装完成标准

- `<archon-dir>` 是有效 Git 检出；
- `pyproject.toml` 显示 Archon 0.3.3；
- `<archon-dir>/.venv/bin/archon version` 成功；
- 已记录源码目录、CLI 路径和当前提交；
- 尚未获得补丁授权时，源码仍保持原版状态。

不要在 OpenCode 安装流程中运行 `archon setup`。它会固定检查并安装 Claude
Code；其他环境依赖按 `environment-zh.md` 分别处理。
