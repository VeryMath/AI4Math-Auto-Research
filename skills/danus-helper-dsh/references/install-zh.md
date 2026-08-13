# 安装并登记 Danus

本流程安装 Danus `v0.1.0-codex`，应用 DeepSeek Harness 适配，接入 DeepSeek
Harness `0.1.0-rc.5` 或 `0.1.0-rc.6`，并保存本机路径。

## 1. 查询安装记录

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" installation-show --json
```

`configured` 与 `valid` 同时为 `true` 时，使用返回的 `danus_home`。记录缺失时，
采用用户指定的安装目录。用户尚未给出目录时，询问安装位置。

## 2. 获取受支持的源码

```text
https://github.com/frenzymath/Danus.git
v0.1.0-codex
7a51336e53cd1d558d0e766a61eb0fed46ebb05b
```

用户确认下载和目标目录后运行：

```bash
git clone https://github.com/frenzymath/Danus.git "$DANUS_HOME"
git -C "$DANUS_HOME" switch -c dsh-adapter \
  7a51336e53cd1d558d0e766a61eb0fed46ebb05b
```

已有仓库依次检查：

```bash
git -C "$DANUS_HOME" status --short
git -C "$DANUS_HOME" branch --show-current
git -C "$DANUS_HOME" rev-parse HEAD
```

应用补丁时，HEAD 应等于支持的 commit，工作区应为空。

## 3. 保存安装路径并登记 Skill

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" \
  installation-set "$DANUS_HOME" --json
python3 "$SKILL_DIR/scripts/danus_helper.py" skill-install --json
```

默认保存位置为：

```text
~/.dsh/danus-helper-dsh.toml
~/.dsh/skills/danus-helper-dsh
```

设置 `DSH_HOME` 后，这两个位置随之改变。第二条命令将当前 Skill 链接到 DeepSeek
Harness 的全局 Skill 目录，因此新项目和新会话都能找到 `$danus-helper-dsh`。

## 4. 应用 DeepSeek Harness 适配

按照 [patch-zh.md](patch-zh.md) 检查补丁状态并执行 `patch-apply`。

## 5. 部署运行环境

Danus bootstrap 会在仓库的 `runtime/` 中创建 Python 环境。PATH 中已有可运行的
DeepSeek Harness rc.5 或 rc.6 时直接复用。源码版 DSH 使用下面的方式登记：

```bash
cd "$DANUS_HOME"
DANUS_DSH_SOURCE_ROOT="<DeepSeek Harness 源码绝对路径>" \
DANUS_DSH_SOURCE_NODE="<该 DSH 使用的 Node.js 绝对路径>" \
DANUS_DSH_SOURCE_HOME="<该 DSH 使用的 DSH_HOME 绝对路径>" \
bash scripts/bootstrap.sh
```

bootstrap 会检查源码入口、依赖、版本和 Node.js，然后在 `runtime/dsh-source/` 写入
启动脚本。源码根目录包含 `.dsh-home/` 时，第三个变量可以省略。PATH 和源码入口都
未登记时，bootstrap 会在 `runtime/dsh/` 安装固定版本
`0.1.0-rc.6`。普通安装运行：

```bash
cd "$DANUS_HOME"
bash scripts/bootstrap.sh
```

模型提供方、模型和凭据沿用用户的 DeepSeek Harness 设置。Danus 的默认值记录在
`config/danus.env.example`，首次研究任务还会通过 `initialize` Skill 收集研究偏好。

启动 DeepSeek Harness Web 和验证服务：

```bash
cd "$DANUS_HOME"
bash scripts/services.sh up verify
bash scripts/doctor.sh
```

默认访问地址为：

```text
http://127.0.0.1:3080
```

`bin/danus-web` 会把工作目录设为 Danus 根目录，使 DeepSeek Harness 自动读取
`AGENTS.md`、`.agents/skills` 和 Danus 的 MCP 配置。

## 6. 完成检查

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" doctor --json
```

完成部署时，关键结果为：

```text
patch_state: installed
deployment_state: ready
dsh_version: 0.1.0-rc.5 或 0.1.0-rc.6
runtime_ready: true
global_skill_ready: true
```

安装阶段不发起模型请求。用户提交首个研究任务后，agent 会报告 provider 和 model，
用户确认后进入研究流程。
