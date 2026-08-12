# 安装 `danus-helper` 并部署 Danus

[Danus](https://github.com/frenzymath/Danus) 由北京大学 AI4Math 团队
FrenzyMath 开发，是一套面向数学研究的多 agent 系统。主 agent 负责制定研究策略和
分配任务，多名 worker 并行寻找证明、引理、反例和已有结果，独立的验证 agent
检查每项数学结论。通过检查的结果进入带有依赖关系的事实图，供后续研究、进展总结
和论文写作使用。

`danus-helper` 是我们为 Danus 编写的 OpenCode Skill。它会安装经过测试的 Danus
版本，加入 OpenCode Desktop 运行方式，准备依赖和本地服务，并登记 Danus 在这台
电脑上的安装路径。完成配置后，新项目和新对话都能找到同一套 Danus。

OpenCode 适配覆盖 Danus 的完整工作流程，包括多 worker 研究、独立验证、事实图、
定时检查、任务恢复、进展总结和论文生成。provider、model 和凭据由 OpenCode
管理。

## 安装 Skill

在 OpenCode Desktop 中新建一个对话，把下面这段话发给 agent。

```text
请帮我安装 `danus-helper` Skill，并按照 Skill 里的说明部署 Danus。

GitHub 仓库
https://github.com/VeryMath/AI4Math-Auto-Research

Skill 路径
skills/danus-helper

请把这个 Skill 安装到 OpenCode 的全局 Skills 目录。安装完成后，完整阅读
`SKILL.md`，然后检查本机是否已经安装 Danus。找到现有安装时请沿用并登记路径；
需要安装时请询问我保存位置。

我全程使用 OpenCode Desktop。请应用 Skill 提供的 OpenCode 适配，完成运行环境
部署和健康检查，并确认新项目和新对话能够找到已登记的 Danus。
```

OpenCode 会读取 `danus-helper`，将它装入全局 Skills 目录，再按照 Skill 中的流程
获取 Danus 源码。当前适配面向上游 release `v0.1.0-codex` 的 commit
`7a51336e53cd1d558d0e766a61eb0fed46ebb05b`。helper 会创建单独的适配分支，应用
OpenCode 补丁，并运行 Python 编译和 Git 差异检查。

部署阶段会准备 Danus 的 Python 环境、Node.js 依赖、OpenCode Server、验证服务、
进展总结和论文生成所需的本地工具。安装结束后，helper 会运行诊断，报告 OpenCode
版本、运行环境、适配状态和各项功能的可用情况。

安装过程不会调用数学研究模型。第一次研究任务开始前，Danus 会报告 provider 和
model，并请求用户确认。

## 安装路径和跨对话使用

Danus 安装完成后，`danus-helper` 会把绝对路径写入用户级配置：

```text
~/.config/opencode/danus-helper.toml
```

以后在其他项目或新对话中调用 `$danus-helper`，Skill 会先读取这条记录，再访问
对应的 Danus 安装。OpenCode 第一次访问项目外的安装目录时，可能请求
`external_directory` 权限。确认弹窗中的路径属于 Danus 安装目录后，为该目录
授予访问权限。

## 检查部署结果

关闭当前对话，在任意项目中新建一个对话，然后输入：

```text
使用 $danus-helper 检查已登记的 Danus。
```

部署成功时，agent 会报告 Danus 路径、支持的上游版本、OpenCode 版本、运行环境、
适配状态和现有研究项目。完整部署的 `deployment_state` 为 `ready`。

随后可以直接提出数学问题：

```text
用 Danus 研究闭图像定理。
```

研究、验证、总结和论文写作过程可参照[闭图像定理示例](danus-closed-graph-example.md)。

## Danus 能做什么

| 功能 | 作用 |
|---|---|
| 研究规划 | 分析问题结构，确定阶段目标，并随研究进展更新任务 |
| 并行 workers | 同时推进证明、引理、反例、边界情况和文献线索 |
| 独立验证 | 逐项检查结论与证明，通过的结果进入事实图 |
| 事实图 | 保存经过验证的事实及其依赖关系，为长时间研究提供共享记忆 |
| 定时检查 | 在当前 OpenCode 对话中定期检查项目，并持续汇报进展 |
| 任务恢复 | 根据项目状态、worker 记忆和 session ID 继续长期任务 |
| 进展总结 | 在研究过程中生成面向数学家的 Markdown 和 PDF 总结 |
| 论文生成 | 从确认的目标事实生成 LaTeX 论文，完成编译、引用检查和数学验证 |
| 多项目管理 | 在同一套 Danus 安装中保存和运行多个独立研究项目 |
