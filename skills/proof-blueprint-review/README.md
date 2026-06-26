# Proof Blueprint Review

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

`proof-blueprint-review` helps a coding agent run a proof-work session for a candidate theorem or proof sketch.

It is not an API wrapper. External verifier services or model APIs are optional tools only when they are available and explicitly useful.

## When To Use It

Use this skill when you have:

- a theorem statement that needs assumptions and scope made explicit;
- a proof sketch that needs a blueprint and gap review;
- a proof-obligation ledger that needs repair hints;
- a draft proof whose status should be judged conservatively.

## What It Produces

The agent should produce `problem_intake.md`, `proof_blueprint.md`, verifier-style review artifacts, `repair_hints.md`, proof-obligation patches, and an acceptance-gate summary.

## Skill Entry Points

Load this package directory when using it directly:

```text
skills/proof-blueprint-review/
```

Core files:

- `SKILL.md`: shared Skill layer and main entrypoint.
- `agents/openai.yaml`: agent metadata.
- `references/agent-mediated-proof-protocol.md`: full proof workflow.
- `references/generation-agent.md`: blueprint generation protocol.
- `references/verification-agent.md`: verifier-style review protocol.
- `references/proof-acceptance-contract.md`: final acceptance gate.

## Installation

Copy this to your coding agent:

```text
Please install the `proof-blueprint-review` skill from https://github.com/VeryMath/AI4Math-Auto-Research.git. Read the package `SKILL.md`, install the declared Skill entrypoint, verify that `$proof-blueprint-review` is discoverable, and tell me whether I need to restart the agent.
```

If you already have this skill repository locally, replace the repository URL
with the local folder path. The coding agent should handle cloning, linking,
configuration, reload/restart checks, and verification.

## Quick Start

```text
Use $proof-blueprint-review.

I have a candidate theorem and proof obligations. Normalize the statement,
write a proof blueprint, run a verifier-style review, produce repair hints and
proof-obligation patches, and do not call the result verified unless the
acceptance gate passes.
```

Useful inputs include a theorem statement, proof sketch, failed proof attempt,
`proof_obligations`, verifier feedback, or a directory of existing proof-state
artifacts.

## How To Interact

Use a checkpoint loop:

```text
candidate theorem or proof artifacts
  -> problem intake
  -> proof blueprint
  -> verifier-style review
  -> repair hints and proof-obligation patches
  -> approve / revise / reject / skip
  -> next proof iteration or acceptance gate
```

Use `approve` to run the proposed next proof step, `revise` to adjust the
statement, route, assumptions, or repair target, `reject` to stop the current
proof route, and `skip` to move past a nonessential phase. The agent should ask
before changing the theorem statement, accepting a black box, discarding a
user-preferred route, launching an external verifier, or reporting a proof as
accepted.

## Artifact Contract

Substantive proof work should create or update:

- `problem_intake.md`
- `proof_blueprint.md`
- `generation_trace.json`
- `verification_report.json`
- `verification_summary.md`
- `repair_hints.md`
- `proof_obligation_patches.json`
- `acceptance_gate.md`

Acceptance requires a matching theorem statement, explicit assumptions and black
boxes, verifier-style or human review evidence equivalent to
`verdict="correct"`, no unresolved `critical_errors`, and no unresolved `gaps`.
Treat this as `accepted_by_review`, not automatically as verified. Use
`externally_verified` only when an external verifier/prover accepted the proof
and its evidence is recorded, and `machine_checked` only when a proof assistant
such as Lean checked the final proof.

## Maintainer Checks

Validate the Skill shape after edits:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/proof-blueprint-review
```

Repository-level adapter checks live in the parent AI4Math Skill Library.
