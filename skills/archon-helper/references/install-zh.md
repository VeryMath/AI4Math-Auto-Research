# 安装并登记 Archon

本阶段负责解析本机安装记录、获取 Archon 源码、创建独立 Python 环境，以及保存
`archon_home`。

## 1. 查询安装记录

运行：

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" installation-show --json
```

输出字段：

- `config_file`：用户级配置文件；
- `archon_home`：Archon 源码根目录；
- `archon_bin`：该目录中虚拟环境的 CLI；
- `archon_bin_ready`：CLI 文件状态；
- `version`：已登记 Archon 版本。

`configured` 与 `valid` 同时为 `true` 时，使用输出路径。记录缺失时，采用用户
指定位置。用户尚未选择目录时，询问安装目标。

## 2. 获取兼容版本

OpenCode 补丁对应 Archon 0.3.3。官方仓库与对应提交为：

```text
https://github.com/frenzymath/Archon.git
5e9ae7615efa0aa2cff11edabd5fbc0d45308fd5
```

用户批准网络操作和目标路径后运行：

```bash
git clone https://github.com/frenzymath/Archon.git "$ARCHON_HOME"
git -C "$ARCHON_HOME" checkout 5e9ae7615efa0aa2cff11edabd5fbc0d45308fd5
```

目标目录应为空目录或尚未创建。已有仓库使用以下命令检查：

```bash
git -C "$ARCHON_HOME" status --short
git -C "$ARCHON_HOME" branch --show-current
git -C "$ARCHON_HOME" rev-parse HEAD
```

## 3. 保存安装路径

确认 `pyproject.toml` 的项目名为 `archon` 后运行：

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" \
  installation-set "$ARCHON_HOME" --json
```

默认配置文件为：

```text
~/.config/opencode/archon-helper.toml
```

系统设置 `XDG_CONFIG_HOME` 时，配置文件位于
`$XDG_CONFIG_HOME/opencode/archon-helper.toml`。

## 4. 创建 Archon CLI 环境

使用 Python 3.10 或更高版本：

```bash
python3 -m venv "$ARCHON_HOME/.venv"
"$ARCHON_HOME/.venv/bin/python" -m pip install -e "$ARCHON_HOME"
"$ARCHON_HOME/.venv/bin/archon" version
```

editable 安装让源码中的 OpenCode 补丁直接进入 `archon` CLI。依赖安装属于网络
操作，执行前说明影响并征得用户同意。

## 5. 从其他项目检查

在当前 OpenCode 工作区运行：

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" doctor . --json
```

检查 `archon_home`、`archon_bin_ready`、版本、补丁状态和当前项目状态。新项目
首次访问 Archon 源码目录时，OpenCode 可能请求 `external_directory` 权限。
向用户展示目标路径，并将访问范围限定在该 Archon 安装目录。

完成后进入 OpenCode 与 Lean 环境配置。
