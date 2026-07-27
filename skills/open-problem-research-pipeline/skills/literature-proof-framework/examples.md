# Literature Proof Framework Skill — 示例

## MWE：对 Vizing 猜想构建证明框架

输入：
```
skill3: 分析 outputs/literature_analysis_reports/VizingConjecture_方法分析报告_2026-07-10.json
```

预期输出应包含多个证明框架，例如：

### 框架一：加权投影优化（改进型）
- **依赖方法**：Clark-Suen 层投影 + Steiner 加权
- **逻辑**：将 Steiner 的常数 c ≈ 0.5643 进一步优化
- **难点**：确定最优加权函数

### 框架二：组合-SOS 融合（融合型）
- **依赖方法**：层投影直觉 + SOS/SDP 代数验证
- **逻辑**：用组合结构降低 SOS 的 SDP 规模
- **难点**：将投影信息编码为多项式约束

### 框架三：全类别图分类证明（分治型）
- **依赖方法**：特殊图类验证 + 一般图约化
- **逻辑**：将图按支配结构分类，逐类攻破
- **难点**：覆盖所有情况