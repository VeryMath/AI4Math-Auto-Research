---
name: open-problem-research-pipeline
description: Research one or more open mathematical problems through a staged literature-search, method-analysis, and proof-framework workflow. Use when a user requests a source-grounded survey of an open problem, a comparison of methods across verified papers, or candidate proof frameworks with explicit evidence and uncertainty boundaries.
---

# Open Problem Research Pipeline

Run a four-part course workflow while keeping literature facts, method
interpretations, and candidate proof ideas distinct.

## Package Map

- `skills/literature-search/`: identify the exact problem and build a
  source-linked literature report.
- `skills/literature-analysis/`: extract and compare methods from the verified
  source packet.
- `skills/literature-proof-framework/`: turn supported methods into candidate
  proof frameworks and explicit proof obligations.
- `skills/qskill/`: route a complete `search -> analysis -> framework -> report`
  run.

Read the relevant nested `SKILL.md` before each stage. Use `qskill` only when
the user asks for the complete pipeline.

## Workflow

1. Normalize the exact problem, graph class or mathematical setting,
   quantifiers, parameter range, and current claimed status.
2. Ask before starting network research when browsing was not already
   requested. Search primary sources first and record URLs and access dates.
3. Produce the literature report under a user-approved output root, defaulting
   to `outputs/literature_reports/`.
4. Analyze only papers whose text or adequate source evidence is available.
   Mark missing method details rather than reconstructing them from titles or
   abstracts.
5. Build candidate proof frameworks. Label every unsupported step as a proof
   obligation; never present a framework as a proof or a proposed variant as
   novel without verification.
6. Assemble Markdown and optional PDF output under `outputs/`. PDF conversion
   is best effort and requires local `pandoc` and XeLaTeX.

## Evidence Contract

- Separate `source states`, `inference`, `candidate direction`, and
  `verified result`.
- Verify citation title, authors, year, venue, and URL before treating a source
  as confirmed.
- Do not infer that a problem remains open from an old survey alone.
- Do not claim novelty, feasibility, or proof completion without the relevant
  literature check or mathematical verification.
- Preserve every intermediate JSON artifact so downstream stages can identify
  exactly what evidence they consumed.

## Outputs

The default package-relative output layout is:

```text
outputs/
├── outputs/literature_reports/
├── outputs/literature_analysis_reports/
├── outputs/literature_proof_reports/
└── outputs/qs_reports/
```

Never overwrite an existing report. Add a version suffix and keep generated
outputs out of git.
