# Research Workflow

## Normalize the Question

Write the exact graph class, conventions, quantifiers, parameter ranges, hypotheses, target conclusion, and what would count as a proof, counterexample, or useful partial result. Separate the user's question from any stronger or weaker reformulation. Record ambiguities and obtain approval for choices that change the problem.

## Literature Search and Priority Limits

Search the most relevant theorem names, graph classes, parameters, constructions, and synonyms. Prioritize primary papers and authoritative bibliographic records; verify citations using `citation-verification.md`. Record databases and sites searched, queries, date, language and year limits, and inaccessible sources. Set a time or query limit in advance. Absence from the searched literature is evidence only about that documented scope, not a novelty proof.

## Reproducible Counterexample Search

State the exact exhaustive universe or sampled range, graph-generation conventions, isomorphism handling, filters, software and version, commands, random seed, hardware-sensitive settings when relevant, and retained logs. Independently check every reported counterexample against all hypotheses and recompute the violated conclusion. Save a compact witness and enough information to reconstruct it.

No counterexample found is not a proof. State the exact exhaustive universe or sampled range, graph-generation conventions, software version, commands, random seed, and logs.

## Proof Development and Proof Audit

Begin with the precise goal and active assumptions. Separate exploratory computations from deductions. For each nontrivial inference, name the definition, hypothesis, earlier result, or verified external theorem used. Audit quantifiers, boundary cases, parameter dependencies, graph conventions, equality cases, and induced/non-induced distinctions. A computation may suggest or test a claim but does not prove an unrestricted theorem unless a justified exhaustive finite reduction covers the full claim.

## Collaborative Proof Verification Loop

This loop is internal to Stage 4 and applies to every proof or counterexample draft. Name successive immutable drafts `proof-v1`, `proof-v2`, and so on. Follow this ordered state machine exactly:

```text
draft -> layered presentation -> invite feedback -> classify and test feedback
-> revise -> full proof/dependency verification -> request exact-version approval
-> repeat unless verification passed AND exact-version approval recorded
```

For layered presentation, give the proof idea first, then numbered steps, and offer user-selected line-by-line expansion of any step. After the first draft and every material revision, explicitly invite questions, objections, and ideas. Treat each user idea as one of four outcomes—correct, partly correct, incorrect, or undetermined—and test it against the active hypotheses, definitions, dependencies, and target before deciding whether to revise. Explain the evidence for the classification; do not accept or reject an idea by tone or authority.

#### Feedback outcome: correct

If the idea is correct, explain its verification and incorporate it into the next proof version, identifying every affected step and dependency.

#### Feedback outcome: partly correct

If the idea becomes valid only under additional hypotheses or restricted scope, state those restrictions explicitly and incorporate only the resulting supported claim; never import the unrestricted idea.

#### Feedback outcome: incorrect

If the idea is incorrect, explain its logical failure or give a verified counterexample and reject it from the proof state. A counterexample must satisfy every active hypothesis and violate the proposed conclusion.

#### Feedback outcome: undetermined

If available evidence cannot decide the idea, keep it unresolved, record the missing evidence or proof obligation, and continue research; do not use it as a dependency.

A material change is any change to a claim, hypothesis, quantifier, construction, dependency, case split, inference, computation, counterexample witness, or conclusion. After every material change, create a new `proof-vN`, invalidate earlier verification and approval for transition purposes, and perform full downstream reverification from the affected location through every dependent lemma, case, computation, witness check, and final conclusion. Local rechecking alone is insufficient.

At every revision, present these four items together for user review: version, changed steps, remaining gaps, and specific review points. The changed-steps list must identify the prior and replacement locations; specific review points must ask about concrete inferences rather than request generic approval.

Complete verification requires all of the following:

1. Restate the exact claim, graph conventions, quantifiers, hypotheses, and parameter range.
2. Check every numbered inference against a definition, active hypothesis, proved local result, reproducible computation, or verified external result with matching hypotheses.
3. Recheck dependency availability and direction, quantifier scope, parameter hierarchy, boundary and equality cases, exhaustive case coverage, and induced/non-induced, directed/undirected, simple/multiple-edge, finite/infinite, and labeled/unlabeled distinctions when relevant.
4. For a counterexample, independently verify every hypothesis and recompute the failed conclusion; for computation, verify the universe or sample, generator conventions, isomorphism handling, code/version/command/seed, retained log, and any claimed finite reduction.
5. Trace the affected location through all downstream dependencies and the final conclusion, record remaining gaps, and set `verification_status=passed` only when none remains.

After verification, request approval using the exact identifier, for example: “Do you explicitly approve `proof-v3`?” The loop exits only when `verification_status=passed` AND explicit approval of the exact `proof-vN` is recorded. Silence and “looks fine” are not approval; vague praise, approval of an older version, or approval given before a later material revision also does not satisfy the condition.

If feedback exposes an error, mark verification failed, preserve the rejected version and concise log, revise if possible, and rerun the loop. If a dependency is unavailable, a check is inconclusive, the user does not explicitly approve the exact version, or a gap cannot be closed within scope, keep the loop unresolved until it qualifies for one of the following mutually exclusive exits:

- **Exit A — proved/verified candidate:** `verification_status=passed` AND explicit approval of the exact `proof-vN` are recorded. This is the only exit that permits a proof candidate to be classified as a proved theorem/lemma or verified counterexample.
- **Exit B — explicitly downgraded unresolved candidate:** the unsupported theorem claim is withdrawn; the exact classification is recorded as partial result, open problem, or computational observation; the precise gap and scope are recorded; and the user explicitly approves the downgrade status and version. Exit B must never be marked as a theorem or proved result, and it cannot inherit verification or approval from Exit A.

Do not produce the Research Audit until every proof/counterexample candidate satisfies all conditions of exactly one exit. A downgrade without the user's exact status/version approval remains unresolved. After this exit check, produce the Research Audit and retain the Stage 4 `[USER GATE]` before any paper drafting.

## Result Classification

Assign every claim exactly one of the following evidence-aware labels. Do not promote a result beyond its evidence.

### Proved theorem or lemma

A complete proof audit checks quantifiers, hypotheses, boundary cases, parameter dependencies, and every nontrivial inference. Every dependency is either proved locally or cited to a verified source whose hypotheses match.

### Verified counterexample

An explicit object satisfies all hypotheses and violates the claimed conclusion; its structure and verification are reproducible.

### Partial result

A rigorously proved statement gives an exact restricted graph class and parameter range, direction, bound, or conditional case. State every restriction prominently and do not generalize beyond it.

### Computational observation

A reproducible calculation establishes behavior only for its stated exhaustive universe or sampled range. Report the range and method. Computation cannot prove an unbounded claim unless a proved finite reduction makes the checked universe exhaustive for that claim.

### Open problem

The claim is unresolved within this documented investigation and literature-search scope. This label does not assert that the problem is recognized as open by the field or that it is novel. The result label itself must state the searched sources, queries, dates, and limits, then summarize what was tried and the principal gaps.

## Research Audit Template

For each result, record:

- **Claim:** exact statement with graph conventions, quantifiers, and parameter range.
- **Evidence type:** one classification above and the concrete proof, witness, or computation supporting it.
- **Verified range:** full theorem domain, restricted cases, exhaustive finite universe, or sampled range.
- **Dependencies:** local lemmas, external results, software, data, and verified citations.
- **Gaps:** missing proof steps, unchecked cases, inaccessible sources, computational limits, or uncertainty.
- **Literature-search scope:** sources, queries, date, priority limits, and exclusions.
- **Recommended paper status:** include as theorem/lemma, include as counterexample, include with an explicit partial/computational label, mention as open, or omit pending verification.

## Stop Conditions

Stop when the approved time/query/computation limits are reached; a verified counterexample settles the proposed universal claim; a complete audited proof is obtained; a required source, definition, or capability is unavailable; or further work would require changing the approved question. Present the research audit and wait for user approval before drafting a paper.
