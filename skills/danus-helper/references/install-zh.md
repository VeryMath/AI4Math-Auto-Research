# 安装并登记 Danus

本阶段获取经过适配测试的 Danus 源码，登记本机安装路径，并完成运行环境部署。安装
过程使用 OpenCode 当前配置，模型请求留到用户提交数学问题之后。

## 1. 查询安装记录

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" installation-show --json
```

`configured` 与 `valid` 同时为 `true` 时，使用返回的 `danus_home`。记录缺失时，
采用用户指定的安装目录。用户尚未指定目录时，询问安装位置。

## 2. 获取支持的源码

上游仓库、release tag 与支持的 commit 为：

```text
https://github.com/frenzymath/Danus.git
v0.1.0-codex
7a51336e53cd1d558d0e766a61eb0fed46ebb05b
```

用户批准网络操作和目标目录后运行：

```bash
git clone https://github.com/frenzymath/Danus.git "$DANUS_HOME"
git -C "$DANUS_HOME" switch -c opencode-adapter \
  7a51336e53cd1d558d0e766a61eb0fed46ebb05b
```

已有仓库依次检查：

```bash
git -C "$DANUS_HOME" status --short
git -C "$DANUS_HOME" branch --show-current
git -C "$DANUS_HOME" rev-parse HEAD
```

源码应用适配前，HEAD 应等于支持的 commit，工作区应为空。

## 3. 保存安装路径

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" \
  installation-set "$DANUS_HOME" --json
```

默认配置文件为：

```text
~/.config/opencode/danus-helper.toml
```

系统设置 `XDG_CONFIG_HOME` 时，配置文件位于
`$XDG_CONFIG_HOME/opencode/danus-helper.toml`。

## 4. 应用 OpenCode 适配

按照 [patch-zh.md](patch-zh.md) 检查并应用补丁。补丁成功后继续部署运行环境。

## 5. 部署运行环境

Danus bootstrap 会创建仓库内的 `runtime/`，安装 Python 依赖，准备 Node.js，并
登记当前 OpenCode 可执行文件。用户批准依赖下载后运行：

```bash
cd "$DANUS_HOME"
bash scripts/bootstrap.sh
```

保留 `DANUS_OPENCODE_MODEL` 的空值时，Danus 使用 OpenCode 默认模型。首次研究
任务开始前，由 Danus 的 `initialize` skill 收集用户偏好并生成
`config/danus.env`。

启动共享 OpenCode Server 与验证服务：

```bash
cd "$DANUS_HOME"
bash scripts/services.sh up verify
bash scripts/doctor.sh
```

报告 OpenCode 版本、共享服务状态、验证服务状态、Danus Python 环境和安装路径。
`doctor.sh` 对论文所需的 LaTeX 引擎和总结所需的 Chrome 给出单独结果。macOS 上
能够自动识别标准位置中的 Google Chrome 或 Chromium。

## 6. 从其他项目检查

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" doctor --json
```

该命令从用户级配置解析 Danus，适合在新项目和新对话中确认已登记的安装。
安装完成时应看到 `patch_state` 为 `installed`、`deployment_state` 为 `ready`、
`runtime_ready` 为 `true`。模型调用留到用户提交首个研究任务并确认 provider 和
model 之后。
