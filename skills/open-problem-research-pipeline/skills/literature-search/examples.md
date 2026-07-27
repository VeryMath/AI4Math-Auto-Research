# Literature Search Skill — 示例

## MWE 1：经典未解决问题

用户输入：
```
skill1: P vs NP 问题
```

预期流程：
1. 分析 → 理论计算机科学/计算复杂性，核心概念：P, NP, NP-complete, polynomial time
2. 搜索 → arXiv (cs.CC), Wikipedia, 相关综述
3. 输出报告 → 已知结果（COOK-LEVIN定理、PH collapses等）、关键方向（电路下界、自然证明障碍、代数化障碍）、当前状态

## MWE 2：猜想求证进展

用户输入：
```
skill1: 孪生素数猜想目前进展
```

预期流程：
1. 分析 → 数论，核心：twin prime, prime gaps, bounded gaps
2. 搜索 → 关注Zhang Yitang (2013), Maynard, Polymath8 等项目
3. 输出报告 → 从Euclid到Zhang到Maynard的突破，目前已知存在无穷多对间隔≤246的素数

## MWE 3：年轻方向

用户输入：
```
skill1: 布尔函数的灵敏度猜想
```

预期流程：
1. 分析 → 计算复杂性/布尔函数分析
2. 搜索 → Huang Hao (2019) 证明 sensitivity conjecture
3. 输出报告 → 该猜想已于2019年被解决，介绍证明方法

## 跨Skill调用示例

在另一个skill的workflow中：

```
## Step X：文献调研
调用 literature-search skill 查询以下问题的文献进展：
"Hadamard矩阵猜想"

等待返回JSON后，解析 known_results 和 key_papers 字段，
用于后续实验对比和论文引用。
```