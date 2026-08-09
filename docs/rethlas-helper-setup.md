# 安装 `rethlas-helper` 并部署 Rethlas

[Rethlas](https://github.com/frenzymath/Rethlas) 由北京大学 AI4Math 团队 FrenzyMath 开发，用于生成和检查自然语言数学证明。原版围绕两个 Codex agent 工作。生成 agent 从 Markdown 文件读取题目并写出证明蓝图，验证 agent 随后检查逻辑、假设和证明缺口。检查意见会送回生成 agent，供下一轮修订使用。

`rethlas-helper` 是我们为 Rethlas 编写的 OpenCode Skill。安装兼容文件以后，Rethlas 的生成 agent 可以在 OpenCode Desktop 中运行。Skill 也会记录 Rethlas 在这台电脑上的安装路径。完成一次配置以后，新项目和新对话都能找到同一套 Rethlas。

## 安装 Skill

在 OpenCode Desktop 中新建一个对话，把下面这段话发给 agent。

```text
请帮我安装 `rethlas-helper` Skill，并按照 Skill 里的说明配置 Rethlas。

GitHub 仓库
https://github.com/VeryMath/AI4Math-Auto-Research

Skill 路径
skills/rethlas-helper

请把这个 Skill 安装到 OpenCode 的全局 Skills 目录。安装完成后，先完整阅读 `SKILL.md`，再按里面的流程执行。

我全程使用 OpenCode Desktop，请选择 OpenCode 兼容方案，让 Rethlas 的生成 agent 在 OpenCode Desktop 中运行。先检查本机是否已经安装 Rethlas。找到现有安装时请沿用并登记路径；需要安装时请询问我保存位置。

请带我完成运行环境和 provider/model 配置。安装 OpenCode 兼容文件以前先征求我的同意。Rethlas 配置完成后，请登记本机安装路径，并检查新项目和新对话能否找到它。

联网安装、仓库修改和第一次模型调用都请先向我确认。
```

OpenCode 会从给出的仓库读取 `rethlas-helper`，将它装入全局 Skills 目录，再按照 Skill 中的说明检查 Python、OpenCode 和已有的 provider 配置。需要下载依赖或修改 Rethlas 仓库时，agent 会先说明将要进行的操作。

配置模型时，agent 会读取 OpenCode 已有的 provider 连接，并请用户选择本次运行使用的 provider 和 model。API 密钥仍由 OpenCode 保存。

Rethlas 安装完成后，`rethlas-helper` 会把安装路径写入用户级配置。以后从其他项目调用 Rethlas 时，Skill 会先读取这条记录，再访问对应的安装目录。OpenCode 第一次访问项目外的安装目录时，可能会请求 `external_directory` 权限。确认弹窗中的路径属于 Rethlas 安装目录后，为该目录授予访问权限。

## 检查部署结果

关闭当前对话，在任意项目中新建一个对话，然后输入下面这句话。

```text
使用 $rethlas-helper 检查已登记的 Rethlas。
```

部署成功时，agent 会找到先前登记的 Rethlas，报告安装路径、运行环境和 OpenCode 兼容状态。随后便可以直接提出“用 Rethlas 证明……”一类任务。具体过程可参照[叶戈洛夫定理示例](rethlas-egorov-example.md)。
