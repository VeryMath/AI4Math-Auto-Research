#!/usr/bin/env python3
"""Create a Codex-native research workspace from an Agent Laboratory run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_agent_laboratory_run import inspect_target_dir, redact_secret, truncate


PHASES = (
    "literature review",
    "plan formulation",
    "data preparation",
    "running experiments",
    "results interpretation",
    "report writing",
)


def fallback_summary(topic: str) -> dict[str, Any]:
    return {
        "ok": False,
        "diagnosis": "codex-native workspace without Agent Laboratory state",
        "target_dir": "",
        "state_path": None,
        "research_topic": topic,
        "phase_status": {phase: False for phase in PHASES},
        "completed_phases": [],
        "incomplete_phases": list(PHASES),
        "stopped_at": "literature review",
        "recoverable": False,
        "recovered": {
            "lit_review_sum": "",
            "plan": "",
            "dataset_code": "",
            "results_code": "",
            "exp_results": "",
            "interpretation": "",
            "report": "",
        },
        "runtime_yamls": [],
        "research_files": [],
    }


def load_summary(target_dir: Path | None, topic: str) -> dict[str, Any]:
    if target_dir is None:
        return fallback_summary(topic)
    try:
        summary = inspect_target_dir(target_dir, include_error_scan=True)
    except Exception:
        return fallback_summary(topic)
    if topic and not summary.get("research_topic"):
        summary["research_topic"] = topic
    return summary


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact_secret(text), encoding="utf-8")


def phase_table(summary: dict[str, Any]) -> str:
    phase_status = summary.get("phase_status", {}) or {}
    lines = ["| Phase | AgentLab done | Codex action |", "| --- | --- | --- |"]
    for phase in PHASES:
        done = bool(phase_status.get(phase))
        action = "audit and reuse" if done else "complete in Codex"
        lines.append(f"| {phase} | {'yes' if done else 'no'} | {action} |")
    return "\n".join(lines)


def render_handoff(summary: dict[str, Any]) -> str:
    topic = truncate(summary.get("research_topic", ""))
    recovered = summary.get("recovered", {}) or {}
    lines = [
        "# Codex Auto-Research Handoff",
        "",
        "## Research Topic",
        "",
        topic or "TBD",
        "",
        "## Run Diagnosis",
        "",
        f"- Status: `{summary.get('diagnosis', 'unknown')}`",
        f"- Agent Laboratory state: `{summary.get('state_path') or 'not found'}`",
        f"- Recoverable partial result: `{bool(summary.get('recoverable'))}`",
        "",
        "## Phase Plan",
        "",
        phase_table(summary),
        "",
        "## Codex Takeover Contract",
        "",
        "- Do not require another LLM API call to finish the research.",
        "- Use recovered Agent Laboratory material as evidence, not as a finished result.",
        "- If literature is incomplete, gather or ask for papers before finalizing claims.",
        "- Write `plan.md` first, then implement `src/experiment.py`, run it locally, save outputs under `outputs/`, and write `report.md`.",
        "- Report any missing API, package, solver, or data dependency as an explicit blocker with a recovery path.",
        "",
        "## Recovered Literature Review",
        "",
        recovered.get("lit_review_sum") or "_No recovered literature review._",
        "",
        "## Recovered Plan",
        "",
        recovered.get("plan") or "_No recovered plan._",
        "",
        "## Recovered Experiment Code",
        "",
        "```python",
        recovered.get("results_code") or "# No recovered experiment code.",
        "```",
        "",
        "## Recovered Results",
        "",
        recovered.get("exp_results") or "_No recovered experiment results._",
        "",
        "## Recovered Report",
        "",
        recovered.get("report") or "_No recovered report._",
        "",
    ]
    return "\n".join(lines)


def render_plan_template(summary: dict[str, Any]) -> str:
    topic = truncate(summary.get("research_topic", ""))
    return "\n".join(
        [
            "# Research Plan",
            "",
            "## Topic",
            "",
            topic or "TBD",
            "",
            "## Literature Grounding",
            "",
            "- Source papers:",
            "- Relevant theoretical claims:",
            "- Gap or practical decision question:",
            "",
            "## Experiment",
            "",
            "- Research question:",
            "- Synthetic or public data:",
            "- Baselines:",
            "- Metrics:",
            "- Expected output files:",
            "",
            "## Execution Checklist",
            "",
            "- [ ] Finalize plan",
            "- [ ] Write `src/experiment.py`",
            "- [ ] Run experiment locally",
            "- [ ] Save outputs under `outputs/`",
            "- [ ] Interpret results",
            "- [ ] Write `report.md`",
            "",
        ]
    )


def render_report_template(summary: dict[str, Any]) -> str:
    topic = truncate(summary.get("research_topic", ""))
    return "\n".join(
        [
            "# Auto-Research Report",
            "",
            "## Objective",
            "",
            topic or "TBD",
            "",
            "## Related Work",
            "",
            "TBD",
            "",
            "## Method",
            "",
            "TBD",
            "",
            "## Experiment",
            "",
            "TBD",
            "",
            "## Results",
            "",
            "TBD",
            "",
            "## Limitations",
            "",
            "TBD",
            "",
            "## Next Steps",
            "",
            "TBD",
            "",
        ]
    )


def write_workspace(summary: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "src").mkdir(exist_ok=True)
    (output_dir / "outputs").mkdir(exist_ok=True)
    (output_dir / "data").mkdir(exist_ok=True)

    recovered = summary.get("recovered", {}) or {}
    files = {
        "research_state.json": json.dumps(summary, indent=2, ensure_ascii=False),
        "codex_handoff.md": render_handoff(summary),
        "literature_review.md": recovered.get("lit_review_sum") or "# Literature Review\n\nTBD\n",
        "plan.md": recovered.get("plan") or render_plan_template(summary),
        "report.md": recovered.get("report") or render_report_template(summary),
        "src/experiment.py": recovered.get("results_code") or "# Fill this with the Codex-native experiment.\n",
    }
    written: list[str] = []
    for relative, content in files.items():
        path = output_dir / relative
        write_text(path, content)
        written.append(str(path))

    return {
        "ok": True,
        "workspace_dir": str(output_dir.resolve()),
        "handoff": str((output_dir / "codex_handoff.md").resolve()),
        "written_files": written,
        "diagnosis": summary.get("diagnosis"),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-dir", type=Path, default=None)
    parser.add_argument("--research-topic", default="")
    parser.add_argument("--output-dir", type=Path, default=Path("codex_research"))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    summary = load_summary(args.target_dir, args.research_topic)
    payload = write_workspace(summary, args.output_dir)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Codex research workspace: {payload['workspace_dir']}")
        print(f"Handoff: {payload['handoff']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
