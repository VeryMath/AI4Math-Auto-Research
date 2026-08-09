# 安装 `archon-helper` 并部署 Archon

[Archon](https://github.com/frenzymath/Archon) 由北京大学 AI4Math 团队 FrenzyMath 开发，用于把研究级数学内容形式化为 Lean 4 项目。原版主要使用 Claude Code，也支持 Codex。它可以读取论文、证明草稿、项目说明和已有 Lean 代码，先整理证明蓝图与定理之间的依赖关系，再经过规划、证明和审查阶段编写 Lean 代码并检查项目构建结果。

`archon-helper` 是我们为 Archon 编写的 OpenCode Skill。它会为 Archon 增加 OpenCode 运行方式，让用户在 OpenCode Desktop 中完成形式化任务。Skill 也会记录 Archon 在这台电脑上的安装路径。用户打开一个 Lean 项目以后，它会同时找到 Archon 安装和当前项目，再把形式化任务交给 Archon。

## 安装 Skill

在 OpenCode Desktop 中新建一个对话，把下面这段话发给 agent。

```text
请帮我安装 `archon-helper` Skill，并按照 Skill 里的说明配置 Archon。

GitHub 仓库
https://github.com/VeryMath/AI4Math-Auto-Research

Skill 路径
skills/archon-helper

请把这个 Skill 安装到 OpenCode 的全局 Skills 目录。安装完成后，先完整阅读 `SKILL.md`，再按里面的流程执行。

我全程使用 OpenCode Desktop。请先检查本机是否已经安装 Archon。找到现有安装时请沿用并登记路径；需要安装时请询问我保存位置。请部署 Skill 支持的 Archon 0.3.3，并安装 OpenCode 兼容文件，让 Archon 在 OpenCode Desktop 中运行。

请带我检查 Python、Lean、Lake 和 OpenCode 环境，再完成 provider/model 配置。Archon 配置完成后，请登记本机安装路径，并检查当前 OpenCode 项目是否已经初始化。

联网安装、源码修改、项目初始化和第一次模型调用都请先向我确认。
```

OpenCode 会从给出的仓库读取 `archon-helper`，将它装入全局 Skills 目录，再按照 Skill 中的说明检查 Archon、Python、Lean、Lake 和 OpenCode。当前 Skill 的兼容文件面向 Archon 0.3.3，并为项目初始化、规划、证明和审查流程登记 OpenCode 运行方式。agent 会在修改 Archon 安装以前说明版本与改动内容。

配置模型时，agent 会使用 OpenCode 已有的 provider 连接，并请用户选择 provider 和 model。第一次调用模型以前，agent 会再次报告本次使用的 provider 和 model，并请求确认。

Archon 安装完成后，`archon-helper` 会把安装路径写入用户级配置。以后新开项目或对话时，Skill 会根据这条记录找到 Archon，再把当前 OpenCode 工作区识别为形式化项目。Archon 位于当前项目外部时，OpenCode 可能会请求 `external_directory` 权限。确认弹窗中的路径属于 Archon 安装目录后，为该目录授予访问权限。

## 检查部署结果

在 OpenCode Desktop 中打开一个准备形式化的项目，新建对话，然后输入下面这句话。

```text
使用 $archon-helper 检查已登记的 Archon 和当前项目。
```

部署成功时，agent 会报告 Archon 的安装路径、OpenCode 兼容状态和当前项目状态。项目尚未初始化时，它会说明准备创建的文件并请求确认。完成初始化以后，就可以直接提出“用 Archon 形式化……”一类任务。具体过程可参照[巴拿赫不动点定理示例](archon-banach-fixed-point-example.md)。
