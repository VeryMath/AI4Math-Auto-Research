# Open Problem Research Pipeline

This package preserves a four-part course design for researching open
mathematical problems:

```text
literature-search
  -> literature-analysis
  -> literature-proof-framework
  -> qskill report assembly
```

Start with [`SKILL.md`](SKILL.md). Each nested skill keeps its submitted
workflow and machine-readable JSON template. The public course edition replaces
machine-local paths with a configurable `outputs/` root, removes generated
reports, and adds evidence and portability guards.

PDF generation is optional:

```bash
python3 skills/qskill/md2pdf.py report.md outputs/qs_reports
```

Set `AI4MATH_CJK_FONT` or pass `--cjk-font` if the local XeLaTeX setup needs an
explicit CJK font.

Course contributor: **Quan Sun**. Released under the repository's MIT License.
See [`PROVENANCE.yaml`](PROVENANCE.yaml) and
[`NORMALIZATION.md`](NORMALIZATION.md).
