# Literature Search Skill

数学问题文献调研技能。输入一个数学公开问题/猜想，自动搜索文献并输出结构化调研报告。

## 单独使用

### 方式1：在opencode.json中配置触发词（推荐）

在 `~/.config/opencode/opencode.json` 中加入：

```json
{
  "skills": {
    "literature-search": {
      "triggers": [
        {"prefix": "skill1:", "description": "数学问题文献搜索（格式: skill1: <问题描述>）"}
      ]
    }
  }
}
```

然后在聊天中直接输入：
```
skill1: 哥德巴赫猜想目前的证明进展如何？
```

### 方式2：在opencode.json中配置command触发

```json
{
  "skills": {
    "literature-search": {
      "command": "skill1:"
    }
  }
}
```

### 方式3：手动加载

在对话中让agent加载本skill：
```
请使用 literature-search skill 帮我查一下：Navier-Stokes方程全局正则性问题
```

## 嵌入到其他Skill中

### 方式A：在opencode.json中配置多skill

```json
{
  "skills": {
    "my-skill": {
      "description": "我的技能",
      "include_skills": ["literature-search"]
    }
  }
}
```

### 方式B：在Agent prompt中引用

在另一个skill的SKILL.md或agent prompt中加入：

```markdown
## 外部skill调用

当需要查阅数学问题文献时，使用 literature-search skill。
调用方式：
1. 在prompt中描述任务："请使用 literature-search skill 查询 {问题}"
2. 触发词：用户输入 "skill1: {问题}" 即进入文献调研流程

输出格式详见 literature-search skill 的 template.json。
```

### 方式C：代码级调用

在另一个skill的workflow中，可以生成类似如下指令让agent执行：

```
请执行 literature-search skill 的工作流：
1. 输入问题：{问题描述}
2. 输出到：outputs/literature_reports/目录
3. 等待返回JSON结果
```

## 输出产物（自动持久化）

每次调用后自动保存到 `outputs/literature_reports/`。

| 文件 | 说明 |
|------|------|
| `<slug>_文献调研报告_<date>.md` | 详细markdown报告 |
| `<slug>_文献调研报告_<date>.json` | 结构化JSON数据，供其他skill消费 |

重复调用时自动添加 `_v2`、`_v3` 后缀避免覆盖。

## MWE（最小工作示例）

用户输入：
```
skill1: 黎曼猜想目前的研究进展
```

Agent将：
1. 识别问题：Riemann Hypothesis（数论）
2. 搜索arXiv/Wikipedia获取已知结果
3. 输出包含以下结构的报告：
   - 问题概述：ζ(s)的非平凡零点都在Re(s)=1/2线上
   - 当前状态：open（未解决）
   - 部分结果：临界线上有无穷多个零点（Hardy, 1914）等
   - 关键文献：相关论文列表
   - 综合评述