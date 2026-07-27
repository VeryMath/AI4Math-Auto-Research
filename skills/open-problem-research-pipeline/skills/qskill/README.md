# QSkill — 完整问题分析管线

## 功能

组合大skill。输入一个或多个数学公开问题，自动执行：
1. **skill1** (literature-search)：文献调研
2. **skill2** (literature-analysis)：方法分析
3. **skill3** (literature-proof-framework)：证明框架构建

输出三合一 PDF 报告。

## 使用方式

```
qskill: Vizing猜想
qskill: 哥德巴赫猜想
qskill: 两个问题：1. 黎曼猜想 2. 孪生素数猜想
```

## 输出产物

自动保存到 `outputs/qs_reports/`

| 文件 | 说明 |
|------|------|
| `<slug>_完整分析报告_<date>.md` | Markdown 源文件 |
| `<slug>_完整分析报告_<date>.pdf` | PDF 文档 |

## 中间产物

执行过程中会自动生成三个子skill的中间产物：

| 路径 | 说明 |
|------|------|
| `outputs/literature_reports/*.json` | skill1 文献调研 |
| `outputs/literature_analysis_reports/*.json` | skill2 方法分析 |
| `outputs/literature_proof_reports/*.json` | skill3 证明框架 |

## 嵌入更大的Skill

读取 `outputs/qs_reports/<slug>_完整分析报告_<date>.json` 中三个字段：
- `problems[0].literature_review` — skill1 结果
- `problems[0].method_analysis` — skill2 结果
- `problems[0].proof_frameworks` — skill3 结果