---
name: extremal-graph-problem-suggester
description: "Use when the user talks about extremal graph theory problems of the form 'forbid X, maximize Y'. The skill reads the user's problem and suggests new variant problems by changing what's forbidden or what's being maximized, so the user can explore fresh research directions. Use this whenever the user mentions Turán-type problems, forbidding subgraphs, or wants research ideas in extremal graph theory — even if they don't explicitly ask for variants."
---

# 极值图论问题变体建议

## 你要做什么

用户给你一个极值图论问题，格式是"禁用子图 A，最大化结构 B"。你先理解清楚 A 和 B 是什么，然后基于你的知识，给出**1个主要推荐 + 1个备选**，每个推荐就是改掉 A 或 B 形成的新问题。

**保持简洁，2-4句话解释理由即可，不要长篇大论。**

## 证据与新颖性边界

- 推荐前检索当前文献，优先使用论文、作者页面、期刊页面或可靠数据库等可核验来源。
- 引用论文前核对标题、作者、年份和链接；无法核对时标为“待核验”，不要编造引用。
- 把输出称为“候选问题”或“候选方向”。未完成系统检索前，不得声称问题是新的或仍然开放。
- “可做”“容易出成果”和“现成技术路线”只能作为待实验判断；必须列出关键未知点、可能已有结果和停止条件。
- 若当前环境不能检索，只能基于用户材料生成带明确 `unverified` 标记的候选清单。

## 最核心的原则：做"小改动"

**不要**建议这些问题（太硬核，难以出成果）：

❌ 超图版本（把图问题推广到超图）
❌ flag algebra / 正则方法 / 吸收法 等技术驱动的方向
❌ 需要全新构造的复杂下界
❌ Ramsey–Turán 这类混合问题
❌ 著名的长期开放问题（除非用户主动问）

**要**建议这些"小改动"：

✅ **改参数**：C_k → C_{k+1}，K_r → K_{r+1}，P_k → P_{k+1} 等
✅ **从一般图限制到二部图**：很多一般图难的问题在二部图上变简单
✅ **从边数改成数三角形**：这是目前最活跃、最容易出成果的方向之一（Alon–Shikhelman 的 generalized Turán），而且往往用现有技术就能做
✅ **从边数改成数 K_4 或其他小团**
✅ **从边数改成谱半径**（近几年很热门，且往往有现成的技术路线）
✅ **稍微改一下禁用条件**：从禁用单个图改成禁用两个图（比如同时禁用 C_4 和 C_5）
✅ **加一个简单的额外条件**：比如在禁用 C_4 的图中考虑"不包含 K_3"的子类

## 替换思路清单（从最简单到稍难）

### 1. 换禁用图（最简单）
- C_k → C_{k+1} 或 C_{k-1}
- K_r → K_{r+1} 或 K_{r-1}
- P_k → P_{k+1}
- C_4 → K_{2,3}（结构与 C_4 相关，但极值数不同）
- 从禁用单个图 → 禁用两个图（如 {C_4, C_5}）

### 2. 换最大化参数
- 边数 → 三角形个数（generalized Turán，最容易出成果）
- 边数 → K_4 个数
- 边数 → C_5 个数
- 边数 → 谱半径
- 边数 → 最小度加边数的混合条件

### 3. 换图类
- 一般图 → 二部图（很多问题变简单）
- 一般图 → 平面图
- n 顶点 → n 顶点 m 边（在给定边数下的极值）

## 输出格式

每个推荐包含三块内容：问题描述、理由（含相关论文）、大概思路

## 主要推荐

**[新问题描述]** 禁用 XXX，最大化 YYY

**为什么：** 2-4句话说明为什么这个变体可能有新结果，**附带1-2篇相关论文**（作者+年份+核心结论即可，不用完整引用格式）

**大概思路：** 简要说明用什么方法可以做。比如"用极图构造+双计数上界"、"用稳定性方法+已知的Turán极图结构分析"、"用谱方法+特征值扰动"等。2-3句话。

## 备选

**[新问题描述]** 禁用 XXX，最大化 YYY

**为什么：** 2-4句话，**附带1-2篇相关论文**

**大概思路：** 2-3句话

每个方案最后补充：

- **证据状态：** `verified` / `partially-verified` / `unverified`
- **下一步核验：** 最小文献检索、边界例计算或已知定理检查
