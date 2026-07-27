# QSkill — 示例

## MWE 1：单个明确问题

用户输入：
```
qskill: Vizing猜想
```

执行流程：
1. skill1 Step 0：问题已明确（Vizing's conjecture），跳过确认
2. skill1：搜索 arXiv/Wikipedia，输出文献调研报告
3. skill2：读取 skill1 输出，提取方法分类（层投影分析、SOS/SDP等）
4. skill3：构建 4 个证明框架（加权投影优化、结构稀疏SOS、分类证明、概率平均投影）
5. 输出 PDF：`outputs/qs_reports/VizingConjecture_完整分析报告_2026-07-10.pdf`

## MWE 2：单个模糊问题

用户输入：
```
qskill: 图论中那个关于乘积的猜想
```

执行流程：
1. skill1 Step 0：搜索发现多个匹配：Vizing猜想、Hadwiger猜想、乘积图着色猜想等
2. 展示给用户："您要问的是 Vizing猜想（γ(G□H) ≥ γ(G)γ(H)）吗？"
3. 用户确认后，继续正常流程

## MWE 3：多个问题

用户输入：
```
qskill: 两个问题。问题1：P vs NP。问题2：Hadamard矩阵猜想
```

执行流程：
- 问题1：独立执行 skill1→skill2→skill3，输出到 `PvsNP_完整分析报告_<date>.pdf`
- 问题2：独立执行 skill1→skill2→skill3，输出到 `HadamardMatrix_完整分析报告_<date>.pdf`
- 同时保存一份综合报告 `MultiProblem_完整分析报告_<date>.pdf`