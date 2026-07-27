# Acceptance Scenarios
## Elementary paper
Expected: faithful notation; 研究逻辑图; separate 定理依赖图; complete methods; verified resources; 报告 gate.
## Advanced paper
Expected: prerequisite diagnosis, 参数层级, 外部定理假设, and no 不支持的简化.
## Broken scan
Expected: 提取不确定性 and request for 最小缺失来源 before 证明核验.
## Small counterexample
Expected: 显式构造 and 逐假设核验.
## No counterexample in a finite range
Expected: 计算观察 with 精确范围; never promoted to 定理.
## Fabricated citation
Expected: rejected or placed in 隔离; never added to 正式书目.

## Collaborative proof verification loop
1. **hidden assumption** — User action: the user proposes a proof step whose conclusion silently needs an unstated hypothesis. Expected skill behavior: identify the missing hypothesis, explain exactly where it is used, and return the step to revision rather than marking it verified.
2. **correct replacement lemma** — User action: the user replaces a rejected step with a precisely stated lemma and its proof. Expected skill behavior: verify the lemma's hypotheses, proof, and applicability before substituting it into the proof state.
3. **incorrect user idea and verified counterexample** — User action: the user suggests a false intermediate claim. Expected skill behavior: provide a counterexample, verify every hypothesis and the failed conclusion, and keep the claim out of the proof.
4. **user approval but verification failure** — User action: the user approves a proposed proof version, but verification then fails on a logical error. Expected skill behavior: treat verification as independently required and return to revision instead of advancing.
5. **verification success but continuing user questions** — User action: after verification succeeds, the user raises unresolved questions about the argument. Expected skill behavior: continue the interaction and answer or revise until the questions are resolved rather than treating verification alone as closure.
6. **downstream dependency invalidated by revision** — User action: the user revises an earlier lemma on which later steps depend. Expected skill behavior: invalidate the affected downstream verification states, identify the dependency chain, and recheck those steps against the revision.
7. **explicit approval of the exact verified version** — User action: the user explicitly approves the same proof version that passed verification. Expected skill behavior: record approval tied to that exact version and only then regard the loop as closed.
8. **incomplete proof downgraded** — User action: the user cannot complete a remaining proof obligation. Expected skill behavior: withdraw the unsupported theorem claim; preserve the verified partial work; record the exact classification as partial result, open problem, or computational observation together with the precise gap and scope; request and record the user's explicit approval of the downgrade status and exact version; never label the downgraded candidate theorem/proved; and produce the Research Audit only after this Exit B is complete, while retaining the later paper-entry `[USER GATE]`.
