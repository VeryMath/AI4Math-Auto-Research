# 安装 Danus：OpenCode 与 DeepSeek Harness

[Danus](https://github.com/frenzymath/Danus) 由北京大学 AI4Math 团队
FrenzyMath 开发，是一套面向数学研究的多 agent 系统。主 agent 负责制定研究策略和
分配任务，多名 worker 并行寻找证明、引理、反例与相关结果，验证 agent 逐项检查
数学结论。通过检查的结果会进入带有依赖关系的事实图，继续用于研究、进展总结和
论文写作。

本仓库为 Danus 准备了两个 Skill：

| 使用环境 | Skill | 研究入口 |
|---|---|---|
| OpenCode Desktop | `danus-helper` | OpenCode Desktop 中的 Danus 项目 |
| DeepSeek Harness | `danus-helper-dsh` | DeepSeek Harness Web 中的 Danus 项目 |

两个 Skill 对应同一个 Danus 上游版本，也覆盖相同的研究流程。安装时，agent 会获取
源码、应用相应适配、准备运行环境、登记本机路径并检查部署状态。完成配置后，新项目
和新对话可以通过对应 Skill 找到已登记的 Danus。

## 在 OpenCode Desktop 中安装

在 OpenCode Desktop 中新建一个对话，发送下面这段话：

```text
请帮我安装下面这个 Skill，并按照 Skill 中的说明部署 Danus。

仓库：https://github.com/VeryMath/AI4Math-Auto-Research
Skill：skills/danus-helper

我使用 OpenCode Desktop。请在安装前询问我 Danus 的保存位置，完成部署和检查，
并登记安装路径。
```

agent 会把 `danus-helper` 安装到 OpenCode 的全局 Skills 目录，读取完整的
`SKILL.md`，然后取得经过适配测试的 Danus 源码。安装路径会记录在：

```text
~/.config/opencode/danus-helper.toml
```

系统设置了 `XDG_CONFIG_HOME` 时，这条记录位于
`$XDG_CONFIG_HOME/opencode/danus-helper.toml`。OpenCode 第一次访问项目目录外的
Danus 安装时，可能会请求访问该目录；确认弹窗中的路径与刚才选择的位置一致即可。

安装完成后，可以换到任意项目并新建对话，输入：

```text
使用 $danus-helper 检查已登记的 Danus。
```

agent 会报告安装路径、适配状态、运行环境和现有研究项目。完整部署的
`deployment_state` 为 `ready`。

## 在 DeepSeek Harness 中安装

在 DeepSeek Harness 中新建一个对话，发送下面这段话：

```text
请帮我安装下面这个 Skill，并按照 Skill 中的说明部署 Danus。

仓库：https://github.com/VeryMath/AI4Math-Auto-Research
Skill：skills/danus-helper-dsh

我使用 DeepSeek Harness。请沿用当前的 DeepSeek Harness 配置，在安装前询问我
Danus 的保存位置，完成部署和检查，并登记安装路径。
```

agent 会安装 `danus-helper-dsh`，检查当前 DeepSeek Harness，取得 Danus 源码并
完成适配。支持的 DeepSeek Harness 版本为 `0.1.0-rc.5` 和 `0.1.0-rc.6`。安装路径
和全局 Skill 默认保存在：

```text
~/.dsh/danus-helper-dsh.toml
~/.dsh/skills/danus-helper-dsh
```

设置了 `DSH_HOME` 时，这两个位置会随之改变。部署完成后，Danus 的研究界面默认
位于：

```text
http://127.0.0.1:3080
```

以后在其他项目或新对话中输入：

```text
使用 $danus-helper-dsh 检查已登记的 Danus。
```

agent 会读取同一条安装记录，报告 Danus 路径、DeepSeek Harness 版本、适配状态和
现有研究项目。

## 两种安装共用的 Danus 版本

当前两个 Skill 都面向 Danus 上游 release `v0.1.0-codex`：

```text
https://github.com/frenzymath/Danus.git
7a51336e53cd1d558d0e766a61eb0fed46ebb05b
```

helper 会在单独的适配分支中完成源码修改，并运行部署检查。provider、model 和凭据
沿用当前 OpenCode 或 DeepSeek Harness 的用户配置。安装流程结束后，Danus 会在
第一次研究任务调用模型前报告 provider 和 model，并请求用户确认。

## 开始研究

部署完成后，向 Danus 直接提交数学问题即可。例如：

```text
用 Danus 研究闭图像定理，给出从 Baire 范畴定理到开映射定理，再到闭图像定理的
完整证明。
```

Danus 会建立研究项目，规划证明路线，分配 workers，验证数学事实，并依据验证意见
继续修订。研究过程中可以随时要求它查看进度、生成中文总结或整理完整论文。

完整运行过程见[闭图像定理使用示例](danus-closed-graph-example.md)。

## Danus 的主要功能

| 功能 | 作用 |
|---|---|
| 研究规划 | 分析问题结构，确定阶段目标，并随研究进展更新任务 |
| 并行 workers | 同时推进证明、引理、反例、边界情况和文献线索 |
| 独立验证 | 逐项检查结论与证明，通过的结果进入事实图 |
| 事实图 | 保存经过验证的事实及其依赖关系，为长时间研究提供共享记忆 |
| 定时检查 | 定期读取项目状态，并在当前会话中汇报进展 |
| 任务恢复 | 根据项目状态、worker 记忆和会话记录继续长期任务 |
| 进展总结 | 生成面向数学家的 Markdown 和 PDF 总结 |
| 论文生成 | 从确认的目标事实生成 LaTeX 论文，完成编译、引用检查和数学验证 |
| 多项目管理 | 在同一套 Danus 安装中保存和运行多个独立研究项目 |
