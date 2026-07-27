# Recoverable State

Create a per-paper state directory with versioned filenames. Never overwrite user files. Record paths, timestamps, hashes when available, evidence status, unresolved items, and `last_approved_gate`.

## Stage Artifacts

| Stage | Required saved state |
|---|---|
| 1 | `intake.md` Markdown and `evidence-index.json` JSON with source locations, evidence labels, uncertainty, and archive hashes. |
| 2 | versioned TeX, compiled PDF, compile/render logs, `question-portfolio.md`, `question-portfolio.json`, and 用户确认记录 for the report gate. |
| 3 | `normalized-question.md` and JSON with exact wording, scope, limits, likely stopping conditions, and 用户确认记录 for the selection gate. |
| 4 | `research-audit.md` and JSON; versioned proof drafts; computation code, raw data, commands, versions, seeds, 代码日志; literature-search log; the Collaborative Proof Verification Loop state and concise proof log below; and 用户确认记录 for the paper-entry gate. |
| 5 | versioned TeX and PDF, bibliography audit, compile/page-render logs, final evidence manifest, and delivery record. |

## Stage 4 Collaborative Proof State

Save these fields after every draft, feedback classification, verification attempt, material revision, and approval request:

```text
current_proof_version
current_proof_path
latest_explicitly_approved_version
verification_status
user_approval_status
proof_log_path
remaining_gaps
downgrade_status
approved_downgrade_classification
approved_downgrade_version
```

Use `proof-vN` identifiers and immutable versioned paths. A material revision resets `verification_status` and `user_approval_status`; approval of an older version never transfers to the new version. `latest_explicitly_approved_version` records only an explicit response naming the exact version, never silence or “looks fine”. For Exit B, set `downgrade_status` only after withdrawing the unsupported theorem claim and recording the precise gap and scope; `approved_downgrade_classification` must be exactly `partial result`, `open problem`, or `computational observation`, and `approved_downgrade_version` records the exact downgraded version explicitly approved by the user. These fields cannot authorize a theorem/proved label.

Keep each concise proof log entry to exactly these nine fields: version; user feedback; affected location; verification method; result; revision decision; remaining gap; verification status; exact-version user approval. Append entries rather than rewriting history.

## Resume Protocol

Append each 用户确认记录 with the approved artifact version and hash. A stage is approved only when the manifest records its gate. On resume, verify manifest and hashes, continue after the 最后批准的 gate, and do 不重读已归档证据. Read only new, changed, unresolved, or integrity-failed evidence. If scope changes, save a new version and return to the affected gate. 不得覆盖用户文件.
