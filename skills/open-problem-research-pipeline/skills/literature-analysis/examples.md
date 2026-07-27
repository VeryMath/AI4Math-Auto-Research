# Literature Analysis Skill — 示例

## MWE 1：链式调用（接续 literature-search）

用户先执行：
```
skill1: Vizing's conjecture
```
得到 `outputs/literature_reports/VizingConjecture_文献调研报告_2026-07-10.json`。

然后执行：
```
skill2: 分析 outputs/literature_reports/VizingConjecture_文献调研报告_2026-07-10.json
```

预期输出：
- **方法分类**：
  - **组合方法**：Clark-Suen 层投影框架、Zerbib 加性改进、Steiner 常数因子突破 → 核心思想：通过改进层中支配集的投影分析，逐步收紧下界
  - **代数方法**：Gaar et al. SOS/SDP → 将猜想转化为多项式非负性检验
  - **计算方法**：Gaar-Siebenhofer Gröbner基 → 对γ=1小规模自动生成证书
- **演化图谱**：Clark-Suen(2000) → Suen-Tarr(2014) → Zerbib(2017) → Steiner(2026)
- **交叉关系**：Gaar的SOS方法独立于组合投影线，提供了验证工具

## MWE 2：用户手动输入文献

用户输入：
```
skill2:
论文1: Clark & Suen (2000). An inequality related to Vizing's conjecture. Electronic J. Combin.
方法：构造一种层投影方案，将Cartesian积的支配集投影到两个因子上，证明γ(G□H) ≥ ½γ(G)γ(H)

论文2: Steiner (2026). A constant-factor step towards Vizing's conjecture. arXiv:2606.14414.
方法：在Clark-Suen框架中引入更精细的层选择和加权投影，将常数提升到(5+√73)/24 ≈ 0.5643
```

预期输出：
- 方法分类：组合方法（同源改进路线）
- 演化关系：Steiner 是 Clark-Suen 的直接改进
- 核心创新：Steiner 的加权选择策略