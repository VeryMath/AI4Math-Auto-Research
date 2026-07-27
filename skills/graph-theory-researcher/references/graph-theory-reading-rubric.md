# Graph Theory Paper Reading Rubric

Use this reference for whole-paper reading, structured notes, notation extraction, theorem dependency mapping, examples, counterexamples, and tightness questions.

## Contents

1. Intake and evidence labels
2. Paper overview rubric
3. Notation table rubric
4. Definitions and results extraction
5. Dependency map guidance
6. Examples, counterexamples, and tightness
7. Reading difficulty diagnosis
8. Quality checks and test scenarios

## 1. Intake and Evidence Labels

Start by identifying the input source:

| Source type | What to trust | What to mark carefully |
|---|---|---|
| PDF text extraction | The extracted text, if coherent | Broken formulas, missing subscripts, page-order errors |
| Screenshot | Visible statements and formulas | OCR uncertainty, cropped hypotheses |
| arXiv title or abstract | Title, authors, abstract claims | Main theorem details not shown in the abstract |
| LaTeX source | Statements and notation | Macros that need expansion |
| User notes | User's interpretation | Whether it matches the paper |
| Proof fragment | Local logic | Global dependencies and earlier definitions |

Use evidence labels:

- `论文明确写道`: directly supported by provided text.
- `根据上下文推测`: likely, but not explicitly confirmed in the provided text.
- `文本中未给出`: unavailable or not present.
- `需要原文确认`: likely sensitive to missing hypotheses, definitions, or notation.

## 2. Paper Overview Rubric

For the first overview, answer these questions without getting trapped in details:

- What is the main object: graph, hypergraph, digraph, random graph, matrix, coloring, matching, minor, family, or parameter?
- What is the problem type: extremal bound, characterization, threshold, spectral inequality, coloring number, Ramsey number, embedding, decomposition, algorithm, stability, construction, or counterexample?
- What known theme is likely involved: Turan-type problem, Ramsey theory, Hall theorem, Menger theorem, Erdos-Renyi random graphs, Szemeredi regularity lemma, container method, spectral radius, expander mixing, graph minors, absorbing method, discharging, or probabilistic method?
- What does the main result appear to improve, generalize, sharpen, or refute?
- What are the prerequisites: undergraduate graph theory, probabilistic method, linear algebra, spectral graph theory, extremal combinatorics, random graph theory, minor theory, or algorithmic graph theory?
- Where is the likely bottleneck: structural reduction, counting estimate, regularity setup, embedding lemma, eigenvalue bound, random model estimate, induction step, extremal construction, or case analysis?

Concise overview format:

```markdown
这篇文章研究的是 ...
主结果大致说明 ...
技术路线看起来是 ...
需要的预备知识包括 ...
最难读的部分可能是 ...
```

## 3. Notation Table Rubric

Maintain a table with enough context to prevent notation drift:

| 符号 | 含义 | 出现位置/上下文 | 标准性 | 潜在混淆 |
|---|---|---|---|---|
| `G` | graph under study | Introduction / theorem statement | Standard | Is it simple, finite, directed? |
| `V(G)` | vertex set | Definitions | Standard | Sometimes paper writes `V` only |
| `E(G)` | edge set | Definitions | Standard | Hypergraph edges may be sets of size `r` |
| `d(v)` | degree of vertex `v` | Local estimates | Standard | Directed graphs may use in/out-degree |
| `delta(G)` | minimum degree | Theorem hypotheses | Standard | Distinguish from small parameter `delta` |
| `Delta(G)` | maximum degree | Bounds | Standard | Different from symmetric difference |
| `N(v)` | neighborhood | Proofs | Standard | Open vs closed neighborhood |
| `N[S]` | closed neighborhood | Domination/connectivity | Standard-ish | Check bracket convention |
| `omega(G)` | clique number | Coloring/Ramsey | Standard | Could mean sample point in probability |
| `alpha(G)` | independence number | Ramsey/coloring | Standard | Also often small parameter |
| `chi(G)` | chromatic number | Coloring | Standard | List chromatic number may differ |
| `g(G)` | girth | Sparse graphs | Standard | Sometimes genus |
| `lambda_i` | eigenvalue | Spectral section | Standard | Matrix and ordering must be stated |
| `rho(G)` | spectral radius | Spectral theorem | Standard | Usually adjacency spectral radius |
| `L(G)` | Laplacian | Spectral section | Standard | Could also be line graph |
| `G(n,p)` | Erdos-Renyi random graph | Random graph results | Standard | Edge independence and p range matter |
| `whp`, `a.a.s.` | with high probability | Random graph statements | Standard | Limit is usually `n -> infinity` |
| `ex(n,H)` | extremal number | Extremal results | Standard | Exact vs asymptotic matters |

For paper-specific symbols, add:

- Original symbol exactly as written.
- Definition in the paper's words if short, otherwise a faithful paraphrase.
- First occurrence or section.
- Whether it conflicts with standard notation or another symbol in the paper.
- A note for likely reader mistakes.

## 4. Definitions and Results Extraction

Extract these objects when present:

- Definitions
- Lemmas
- Propositions
- Theorems
- Corollaries
- Claims
- Observations
- Cases
- Conjectures
- Remarks
- Examples and counterexamples

For each result, record:

| Field | What to write |
|---|---|
| 编号 | The paper's number, such as Theorem 1.2 |
| 类型 | theorem, lemma, proposition, claim, etc. |
| 简洁改写 | A faithful restatement, preserving hypotheses |
| 前提条件 | Graph class, parameters, quantifiers, ranges |
| 结论 | Exact conclusion, bound, existence, algorithm, threshold |
| 依赖 | Definitions, previous results, external theorems |
| 作用 | Why it matters for the main theorem |
| 方法标签 | induction, double counting, spectral method, etc. |
| 风险点 | Missing context, notation ambiguity, likely misread |

Useful proof method tags:

- induction
- contradiction
- minimal counterexample
- extremal choice
- double counting
- probabilistic method
- first/second moment
- Lovasz local lemma
- martingale or concentration
- linear algebra
- spectral method
- eigenvalue interlacing
- regularity lemma
- counting lemma
- absorbing method
- discharging
- container method
- stability argument
- compactness
- minor theory
- switching argument
- augmenting path
- max-flow/min-cut
- randomized construction
- blow-up construction

## 5. Dependency Map Guidance

Use an ASCII tree or ordered list. Keep it honest: if dependencies are inferred rather than explicit, say so.

Example:

```text
Main Theorem 1.3
|- Definition 2.1: admissible graph family
|- Lemma 2.3: structural reduction
|  |- Claim 2.2: neighborhood bound
|  `- Proposition 1.5: known embedding lemma
|- Lemma 3.1: counting estimate
`- Construction 4.1: lower bound / sharpness
```

Also explain flow in prose:

- `Lemma 2.3` reduces the theorem to a dense/sparse/regular/minimal case.
- `Lemma 3.1` supplies the numerical estimate needed after the reduction.
- `Construction 4.1` shows the bound cannot be improved beyond a stated order or constant.

## 6. Examples, Counterexamples, and Tightness

Actively search for:

- Extremal construction
- Sharpness example
- Lower-bound construction
- Forbidden subgraph example
- Random construction
- Blow-up construction
- Complete graph, complete bipartite graph, cycle, tree, expander, random graph
- Counterexample to a stronger statement
- Boundary case where equality holds
- Small-n illustration

For each construction, answer:

- What is the construction?
- Which theorem, bound, or hypothesis does it test?
- Why does it satisfy the hypotheses?
- Why does it block a stronger conclusion?
- Is the result tight, asymptotically tight, order-tight, constant-tight, or not shown tight?
- Can a small example or picture-like verbal description explain it?

Tightness answer template:

```markdown
从提供文本看，tightness 的证据是 ...
这个构造是 ...
它满足定理假设，因为 ...
它使结论不能加强到 ...，因为 ...
所以该结果是 exact tight / asymptotically tight / order-tight / 未确认 tight。
仍需检查 ...
```

## 7. Reading Difficulty Diagnosis

For undergraduate graph theory readers:

- Start with definitions, examples, theorem statements, and simple constructions.
- Delay technical proofs involving regularity, containers, concentration inequalities, spectral interlacing, or minor decompositions.
- Ask for concrete small graphs: paths, cycles, complete graphs, bipartite graphs, trees.

For graduate readers:

- Identify the main theorem, core reduction lemma, technical lemma, and extremal construction.
- Read proofs in dependency order rather than page order when needed.
- Focus on the proof bottleneck and the paper's novelty.

For readers trying to reproduce the proof:

- Build a dependency checklist.
- Rewrite each lemma in their own notation.
- Verify all parameter hierarchies.
- Re-derive key inequalities independently.
- Reconstruct examples and boundary cases.
- Keep a list of external theorems and prerequisites.

Sections that may be skippable on first pass:

- Long technical estimates after their role is understood.
- Historical remarks not needed for proof flow.
- Variants or appendices not used in the main theorem.

Sections usually not skippable:

- Custom definitions.
- Main theorem statements.
- Structural reduction lemmas.
- Claims inside the proof of the main theorem.
- Extremal constructions or counterexamples.

## 8. Quality Checks and Test Scenarios

Run these mental tests before delivering:

1. If the user asks "帮我读这篇 extremal graph theory paper，先给我主定理和 proof roadmap", the answer should include the research problem, main theorem, dependency map, and proof roadmap.
2. If the user posts a lemma proof and asks "这一步为什么成立?", the answer should explain that step, name the dependency or hypothesis, and state what context remains unverified.
3. If the user asks "帮我整理 notation table", the answer should include symbol, meaning, context, standardness, and possible confusion.
4. If the user asks "这个定理 tight 吗?", the answer should look for constructions, lower bounds, counterexamples, or sharpness discussion before concluding.
5. If the user gives no paper content and only says "帮我读一篇图论文章", the answer should not fabricate content and should request title, PDF, LaTeX, abstract, or theorem/proof text.
