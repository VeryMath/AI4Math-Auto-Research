# Literature Proof Framework Skill

基于 literature-analysis（skill2）的方法分析报告，为原始数学问题构建多个可行的证明框架/解决方案框架。

## 单独使用

### 方式1：链式调用（接在 skill2 之后）

```
skill3: 分析 outputs/literature_analysis_reports/VizingConjecture_方法分析报告_2026-07-10.json
```

### 方式2：用户手动输入方法信息

```
skill3:
原始问题: Vizing猜想: γ(G□H) ≥ γ(G)γ(H)
方法1: 层投影分析法，Clark-Suen框架，目前已到0.5643
方法2: SOS/SDP代数方法，仅γ=1有效
...
```

## 嵌入更大的Skill

在外部skill的prompt中加入：

```markdown
## 证明框架构建

使用 literature-proof-framework skill：
1. 输入：outputs/literature_analysis_reports/*.json（来自 skill2）
2. 输出：outputs/literature_proof_reports/*.json（含多个证明框架）
3. 消费：读取 frameworks 数组，每个框架含 logic_chain（逻辑步骤链）
```

## 输出产物

自动保存到 `outputs/literature_proof_reports/`

| 文件 | 说明 |
|------|------|
| `<slug>_证明框架报告_<date>.md` | 详细报告 |
| `<slug>_证明框架报告_<date>.json` | 结构化JSON |

## 框架类型

| 类型 | 含义 |
|------|------|
| 改进型 | 在现有最佳方法上做增量优化 |
| 融合型 | 将两种独立方法结合 |
| 降维型 | 将原问题转化为更简单的问题 |
| 突破型 | 引入全新方法范式 |
| 分治型 | 分解为若干子问题分别处理 |