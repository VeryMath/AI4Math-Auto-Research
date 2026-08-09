# 安装并登记 Rethlas

本阶段负责解析已登记路径、定位现有仓库、克隆 Rethlas，以及保存本机安装路径。

## 1. 查询本机安装记录

将 `SKILL_DIR` 设为主 `SKILL.md` 所在目录，然后运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" installation-show --json
```

输出中的 `config_file` 是用户级配置文件，`rethlas_home` 是已登记的 Rethlas
仓库根目录。`configured` 和 `valid` 同时为 `true` 时，直接将该路径设为
`TARGET`。

记录缺失时，使用用户指定目录。用户尚未选择目录时，询问安装位置。记录失效
时，报告原路径与错误，并请用户提供移动后的目录或新的安装位置。

## 2. 识别 Rethlas 仓库

有效仓库根目录包含：

- `agents/generation/AGENTS.md`
- `agents/generation/.codex/config.toml`
- `agents/verification/AGENTS.md`
- `agents/verification/.codex/config.toml`

检查指定目录：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor "$TARGET" --json
git -C "$TARGET" status --short
git -C "$TARGET" branch --show-current
git -C "$TARGET" remote -v
```

报告仓库结构、已有改动和 origin。维护用户已有的 tracked 与 untracked 文件。

## 3. 获取 Rethlas

用户指定仓库地址时使用该地址。默认上游为：

```bash
git clone https://github.com/frenzymath/Rethlas.git "$TARGET"
```

克隆属于网络操作，执行前征得用户同意。目标目录应为空目录或尚未创建。完成后
再次运行 doctor，确认该目录能够被识别为 Rethlas 根目录。

## 4. 保存安装路径

仓库根目录识别成功后运行：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" installation-set "$TARGET" --json
```

该命令把绝对路径写入：

```text
~/.config/opencode/rethlas-helper.toml
```

系统设置 `XDG_CONFIG_HOME` 时，配置文件位于
`$XDG_CONFIG_HOME/opencode/rethlas-helper.toml`。

随后从任意工作目录检查登记结果：

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor --json
```

新项目首次访问该目录时，OpenCode 可能显示 `external_directory` 权限请求。
向用户说明目标路径，并将授权范围限定为该 Rethlas 仓库。

## 阶段完成

确认以下信息：

- 配置文件路径；
- `rethlas_home` 绝对路径；
- 仓库 origin 与当前分支；
- doctor 能从其他工作目录解析该安装。

随后进入 OpenCode 环境配置阶段。
