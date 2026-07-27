# Literature Analysis Skill

对 literature-search 输出的文献调研结果进行深度方法分析：提取每篇文献的证明方法和技术思想，按数学范畴分类，输出结构化分析报告。

## 单独使用

### 方式1：链式调用（接在 literature-search 之后）

先运行 skill1，再将输出的 JSON 文件传递给本skill：

```
请对我刚才查到的文献结果做方法分析
```

或手动指定文件：

```
skill2: 分析 outputs/literature_reports/VizingConjecture_文献调研报告_2026-07-10.json
```

### 方式2：用户手动输入多篇文献

```
skill2:
论文A: ... (标题、作者、方法简述等)
论文B: ...
论文C: ...
```

## 嵌入到其他Skill

在另一个skill的SKILL.md或agent prompt中加入：

```markdown
## 外部skill调用

当需要对文献调研结果进行方法分析时，使用 literature-analysis skill。

**链式调用流程**：
1. 调用 literature-search（skill1:）获得文献调研JSON
2. 读取 outputs/literature_reports/*.json
3. 调用 literature-analysis 分析该JSON
4. 输出到 outputs/literature_analysis_reports/ 目录

**格式**：分析报告输出JSON包含 method_classification（按方法大类分组）、innovation_flow（演化关系）、method_timeline（时间线）等字段。
```

## 输出产物（自动持久化）

每次调用后自动保存到 `outputs/literature_analysis_reports/`。

| 文件 | 说明 |
|------|------|
| `<slug>_方法分析报告_<date>.md` | 详细方法分析报告 |
| `<slug>_方法分析报告_<date>.json` | 结构化JSON数据 |

## 方法分类体系

| 一级分类 | 技术路线举例 |
|----------|-------------|
| 组合方法 | 投影分析、双计数、极值构造、层分解 |
| 代数方法 | SOS/SDP、Gröbner基、多项式方法、表示论 |
| 概率方法 | 随机图、概率不等式、Lovász局部引理 |
| 分析方法 | 不等式估计、渐近分析、泛函分析 |
| 计算方法 | 半定规划、数值验证、计算机搜索 |
