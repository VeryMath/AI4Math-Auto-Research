# Proof Analysis Checklist

Use this reference for theorem, lemma, proposition, claim, proof fragment, dependency checking, and "why does this step hold?" questions.

## Contents

1. Normalize the statement
2. Locate the proof step
3. Build the proof skeleton
4. Check dependencies and hidden assumptions
5. Method-specific checks
6. Explain difficult steps
7. Short answer templates

## 1. Normalize the Statement

Before analyzing a proof, restate:

- Goal: exactly what must be proved.
- Quantifiers: for all, exists, sufficiently large, with high probability, for every epsilon, there exists delta.
- Objects: graph type, vertex count, edge count, degree assumptions, forbidden subgraphs, coloring, matching, matrix, random model.
- Parameters: order of choice and hierarchy, such as `0 < 1/n << delta << epsilon << 1`.
- Conclusion type: equality, inequality, existence, uniqueness, algorithmic output, probability bound, threshold, stability, embedding, decomposition, or contradiction.

If the theorem statement is missing, ask for it or state that only local verification is possible.

## 2. Locate the Proof Step

For a proof fragment, identify:

- What was already assumed before this step?
- Is the proof using contradiction, induction, minimal counterexample, maximal choice, or case analysis?
- What local object has just been constructed?
- What does this step need to establish for the next step?
- Which previous lemma, definition, or inequality is likely being invoked?

Answer order for "这一步为什么成立?":

1. Restate the disputed step.
2. Name the condition or previous result that justifies it.
3. Translate the step into graph language.
4. Give the algebra or combinatorial derivation.
5. State any missing context that could invalidate the explanation.

## 3. Build the Proof Skeleton

For complex proofs, separate four layers:

### One-paragraph proof idea

Explain the route in plain language: reduce to a cleaner structure, construct an auxiliary object, count two ways, find a forbidden configuration, apply a spectral inequality, or expose a random graph in stages.

### Step-by-step skeleton

Use numbered steps:

1. Set up assumptions and choose parameters.
2. Define the key object or extremal/minimal counterexample.
3. Prove structural claims.
4. Apply the main technical lemma or method.
5. Convert the technical output into the target conclusion.
6. Handle boundary cases and conclude.

### Technical lemmas used

List each lemma with its role, not just its number.

### Why this works

Explain the pressure mechanism: degree forces expansion, forbidden subgraphs limit neighborhoods, eigenvalues control edge distribution, random choice produces the desired object, or extremality forbids a local improvement.

## 4. Check Dependencies and Hidden Assumptions

For every nontrivial line, ask:

- Does it use simple graph assumptions?
- Does it require connectedness, bipartiteness, regularity, finiteness, orientation, uniformity, or inducedness?
- Does the inequality depend on integer rounding, floors, ceilings, or sufficiently large `n`?
- Are all constants chosen in the correct order?
- Is the graph allowed to be empty, disconnected, complete, or small?
- Is a neighborhood open or closed?
- In directed graphs, is this in-neighborhood, out-neighborhood, or total degree?
- In hypergraphs, is degree vertex-degree, codegree, or edge-degree?
- In probability, is the event independent, conditionally independent, or exposed by a filtration?
- In spectral arguments, is the vector normalized and is the matrix symmetric?
- Is an external theorem being used with all its hypotheses satisfied?

Common misread risks:

- Exact result versus asymptotic result.
- Necessary versus sufficient condition.
- Induced subgraph versus subgraph.
- Minor versus topological minor.
- Vertex cut versus edge cut.
- Matching size versus matching number.
- Edge coloring versus vertex coloring.
- `G(n,p)` versus `G(n,m)`.
- Adjacency spectral radius versus Laplacian eigenvalue.

## 5. Method-Specific Checks

### Induction

- State induction parameter.
- Check base case.
- Verify the reduced object remains in the same class.
- Confirm the conclusion lifts back to the original graph.

### Contradiction or minimal counterexample

- State the minimality criterion.
- Check why a local modification creates a smaller or better counterexample.
- Verify no hypothesis is lost after deletion, contraction, recoloring, or switching.

### Double counting

- Identify the set of pairs, triples, paths, copies, or incidences counted.
- Write both counts explicitly.
- Check overcounting and equality/inequality directions.

### Probabilistic method

- State the random experiment and model.
- Define random variables and events.
- Check expectation, variance, concentration, union bound, or local lemma conditions.
- Clarify whether the conclusion is existence, whp, or threshold behavior.

### Spectral method

- State the matrix: adjacency, Laplacian, normalized Laplacian, signless Laplacian, or quotient matrix.
- State eigenvalue ordering and normalization.
- Check whether the graph is regular or whether Perron-Frobenius applies.
- Explain how the spectral inequality translates into graph structure.

### Regularity, containers, or absorbing

- Record the parameter hierarchy.
- Identify the reduced graph, container family, or absorbing structure.
- Separate the high-level idea from long technical estimates.
- Check which exceptional sets are discarded and how their size is controlled.

### Matching and connectivity

- For Hall-type arguments, identify the subset `S` and verify `|N(S)| >= |S|`.
- For augmenting paths, show why the path exists and why augmentation improves the matching.
- For Menger-type arguments, distinguish vertex-disjoint and edge-disjoint paths.
- For cuts, verify minimality and whether endpoints are counted.

### Coloring and Ramsey

- State whether coloring is vertex, edge, list, fractional, acyclic, or proper coloring.
- Track color classes and forbidden monochromatic structures.
- Check whether a recoloring argument preserves all constraints.

### Minors and structural graph theory

- Distinguish deletion, contraction, subdivision, immersion, and topological minor.
- Check whether branch sets are disjoint and connected.
- Track treewidth, separators, and decomposition bags precisely.

### Algorithms

- State input size and representation.
- Identify invariant, termination measure, and correctness proof.
- Check complexity and whether randomized steps are Monte Carlo or Las Vegas.

## 6. Explain Difficult Steps

Use this pattern:

```markdown
这一步的目标是 ...
当前已经知道 ...
用到的定义/引理是 ...
把它翻译成图论语言就是 ...
因此可以推出 ...
容易误解的是 ...
如果用一个小例子看 ...
仍需原文确认的是 ...
```

For inequalities:

1. Say what is being bounded: edges, copies of a subgraph, degrees, common neighborhoods, eigenvalues, bad events, color classes.
2. Explain why the bound is plausible graph-theoretically.
3. Then show the algebra.
4. Check equality cases or lost constants if tightness matters.

For constructions:

1. Name the constructed graph or auxiliary object.
2. Explain why it satisfies the proof's hypotheses.
3. Explain what property it forces.
4. Explain how it moves the proof closer to the target.

## 7. Short Answer Templates

### Step explanation

```markdown
这一步成立的原因是 ...
它用到的条件是 ...
具体推导为 ...
图论直觉是 ...
需要注意 ...
```

### Proof roadmap

```markdown
证明目标：...
路线概括：...
步骤 1：...
步骤 2：...
关键瓶颈：...
最后如何收束：...
```

### Dependency check

```markdown
这一步依赖：
- Definition ...
- Lemma ...
- Assumption ...

没有看到它依赖：
- ...

仍需确认：
- ...
```

### Possible gap report

```markdown
这里可能有缺口，因为 ...
要补上它，需要证明 ...
可尝试使用 ...
如果原文前面已有 ...，则该步可以成立。
```
