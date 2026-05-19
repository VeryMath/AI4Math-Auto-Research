#!/usr/bin/env python3
"""Inspect an Agent Laboratory run and recover useful partial results."""

from __future__ import annotations

import argparse
import json
import os
import pickle
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


PHASE_ORDER = (
    "literature review",
    "plan formulation",
    "data preparation",
    "running experiments",
    "results interpretation",
    "report writing",
    "report refinement",
)
AGENT_NAMES = ("phd", "postdoc", "professor", "ml_engineer")
RECOVERABLE_ATTRS = (
    "lit_review_sum",
    "plan",
    "dataset_code",
    "results_code",
    "exp_results",
    "interpretation",
    "report",
)
ERROR_PATTERNS = (
    "Internal Server Error",
    "ReadTimeout",
    "ConnectTimeout",
    "ConnectionError",
    "Connection refused",
    "TIMEOUT:",
    "Timeout",
    "timed out",
    "Max tries during phase",
    "Traceback",
)
TEXT_EXTENSIONS = {".log", ".md", ".txt", ".json", ".yaml", ".yml", ".out", ".err"}


def redact_secret(text: str) -> str:
    text = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-<redacted>", text)
    text = re.sub(r"(?i)(Bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1<redacted>", text)
    return text


def truncate(text: Any, limit: int = 4000) -> str:
    if text is None:
        return ""
    value = redact_secret(str(text))
    if len(value) <= limit:
        return value
    return value[:limit] + f"\n... <truncated {len(value) - limit} chars>"


def resolve_target_dir(path: Path) -> Path:
    path = path.expanduser().resolve()
    if (path / "ai_lab_repo.py").exists():
        return path
    nested = path / "external" / "agent-laboratory"
    if (nested / "ai_lab_repo.py").exists():
        return nested
    return path


def infer_run_root(target_dir: Path) -> Path:
    if target_dir.name == "agent-laboratory" and target_dir.parent.name == "external":
        return target_dir.parent.parent
    return target_dir


def find_latest_state(target_dir: Path) -> Path | None:
    state_dir = target_dir / "state_saves"
    if not state_dir.exists():
        return None
    states = sorted(state_dir.glob("Paper*.pkl"), key=lambda item: item.stat().st_mtime, reverse=True)
    return states[0] if states else None


def load_workflow_state(target_dir: Path, state_path: Path) -> Any:
    sys.path.insert(0, str(target_dir))
    with state_path.open("rb") as handle:
        return pickle.load(handle)


def candidate_pythons(target_dir: Path) -> list[Path]:
    candidates = [
        target_dir / ".venv" / "bin" / "python",
        Path("/opt/anaconda3/envs/ai4math-agent-lab/bin/python"),
    ]
    return [path for path in candidates if path.exists() and path.resolve() != Path(sys.executable).resolve()]


def reexec_with_runtime_python(target_dir: Path, argv: list[str]) -> int | None:
    if os.environ.get("AI4MATH_INSPECTOR_REEXEC"):
        return None
    for python in candidate_pythons(target_dir):
        env = dict(os.environ)
        env["AI4MATH_INSPECTOR_REEXEC"] = "1"
        result = subprocess.run([str(python), str(Path(__file__).resolve()), *argv], env=env, check=False)
        return result.returncode
    return None


def agent_attr(workflow: Any, attr: str) -> str:
    for agent_name in AGENT_NAMES:
        agent = getattr(workflow, agent_name, None)
        if agent is None or not hasattr(agent, attr):
            continue
        value = getattr(agent, attr)
        if value:
            return truncate(value)
    return ""


def summarize_workflow_state(workflow: Any, state_path: Path | None = None) -> dict[str, Any]:
    phase_status = dict(getattr(workflow, "phase_status", {}) or {})
    completed = [phase for phase in PHASE_ORDER if phase_status.get(phase)]
    incomplete = [phase for phase in PHASE_ORDER if not phase_status.get(phase)]
    stopped_at = incomplete[0] if incomplete else None
    recovered = {attr: agent_attr(workflow, attr) for attr in RECOVERABLE_ATTRS}
    reference_papers = getattr(workflow, "reference_papers", []) or []
    literature_count = len(getattr(workflow, "phd", object()).lit_review) if hasattr(getattr(workflow, "phd", None), "lit_review") else 0
    if not literature_count:
        literature_count = len(reference_papers)

    recoverable = bool(recovered.get("lit_review_sum") or recovered.get("plan") or reference_papers)
    diagnosis = "completed" if not stopped_at else f"incomplete: stopped before or during {stopped_at}"
    if stopped_at and completed == ["literature review"]:
        diagnosis = "incomplete: literature review finished, but no executable experiment or report was produced"

    return {
        "ok": stopped_at is None,
        "diagnosis": diagnosis,
        "state_path": str(state_path) if state_path else None,
        "research_topic": truncate(getattr(workflow, "research_topic", "")),
        "phase_status": phase_status,
        "completed_phases": completed,
        "incomplete_phases": incomplete,
        "stopped_at": stopped_at,
        "statistics_per_phase": getattr(workflow, "statistics_per_phase", {}) or {},
        "num_papers_lit_review": getattr(workflow, "num_papers_lit_review", None),
        "reference_paper_count": len(reference_papers),
        "literature_review_item_count": literature_count,
        "max_steps": getattr(workflow, "max_steps", None),
        "mlesolver_max_steps": getattr(workflow, "mlesolver_max_steps", None),
        "papersolver_max_steps": getattr(workflow, "papersolver_max_steps", None),
        "recoverable": recoverable,
        "recovered": recovered,
    }


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    if not root.exists():
        return files
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if ".git" in parts or ".venv" in parts or "__pycache__" in parts:
            continue
        if "recovery_report" in path.name:
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            files.append(path)
    return files


def scan_error_evidence(roots: list[Path], max_items: int = 25) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[Path] = set()
    for root in roots:
        for path in iter_text_files(root):
            if path in seen:
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if any(pattern in line for pattern in ERROR_PATTERNS):
                    evidence.append(
                        {
                            "file": str(path),
                            "line": str(line_no),
                            "text": truncate(line.strip(), 700),
                        }
                    )
                    if len(evidence) >= max_items:
                        return evidence
    return evidence


def inspect_target_dir(path: Path, include_error_scan: bool = True) -> dict[str, Any]:
    target_dir = resolve_target_dir(path)
    run_root = infer_run_root(target_dir)
    latest_state = find_latest_state(target_dir)
    runtime_yamls = sorted(str(path) for path in (target_dir / ".ai4math_runs").glob("*.yaml"))
    research_files = sorted(str(path) for path in (target_dir / "MATH_research_dir").rglob("*") if path.is_file())
    payload: dict[str, Any] = {
        "target_dir": str(target_dir),
        "run_root": str(run_root),
        "runtime_yamls": runtime_yamls,
        "research_files": research_files,
    }
    if latest_state is None:
        payload.update(
            {
                "ok": False,
                "diagnosis": "no Agent Laboratory state_saves/Paper*.pkl file found",
                "recoverable": False,
            }
        )
    else:
        workflow = load_workflow_state(target_dir, latest_state)
        payload.update(summarize_workflow_state(workflow, latest_state))

    if include_error_scan:
        payload["error_evidence"] = scan_error_evidence([run_root, target_dir])
    return payload


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Agent Laboratory Run Diagnosis",
        "",
        f"- Target dir: `{summary.get('target_dir', '')}`",
        f"- State: `{summary.get('state_path') or 'not found'}`",
        f"- Status: `{summary.get('diagnosis', 'unknown')}`",
        f"- Recoverable partial result: `{bool(summary.get('recoverable'))}`",
        "",
        "## Phase Status",
        "",
        "| Phase | Done |",
        "| --- | --- |",
    ]
    phase_status = summary.get("phase_status", {}) or {}
    for phase in PHASE_ORDER:
        lines.append(f"| {phase} | {'yes' if phase_status.get(phase) else 'no'} |")

    lines.extend(["", "## Recovered Content", ""])
    recovered = summary.get("recovered", {}) or {}
    for attr in RECOVERABLE_ATTRS:
        value = recovered.get(attr) or ""
        if value:
            lines.extend([f"### {attr}", "", value, ""])
        else:
            lines.extend([f"### {attr}", "", "_No content recovered._", ""])

    evidence = summary.get("error_evidence", []) or []
    if evidence:
        lines.extend(["## Error Evidence", ""])
        for item in evidence:
            lines.append(f"- `{item['file']}:{item['line']}` {item['text']}")
        lines.append("")

    lines.extend(
        [
            "## Recommended Handling",
            "",
            "- If any research phase after literature review is incomplete, do not present the run as a finished Auto-Research result.",
            "- Use the recovered literature review as seed material, then either rerun with a more stable backend or let the coding agent synthesize a plan, experiment, and report from the recovered state.",
            "- If the evidence shows backend 500/timeout/connection failures, treat the primary fault as model gateway reliability rather than a conda or Agent Laboratory deployment failure.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-dir", type=Path, default=Path("external/agent-laboratory"))
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--no-error-scan", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else argv
    args = parse_args(raw_argv)
    try:
        summary = inspect_target_dir(args.target_dir, include_error_scan=not args.no_error_scan)
    except ModuleNotFoundError as exc:
        target_dir = resolve_target_dir(args.target_dir)
        rerun_code = reexec_with_runtime_python(target_dir, raw_argv)
        if rerun_code is not None:
            return rerun_code
        summary = {
            "ok": False,
            "target_dir": str(target_dir),
            "diagnosis": f"failed to inspect run: {exc}",
            "recoverable": False,
        }
    except Exception as exc:
        summary = {
            "ok": False,
            "target_dir": str(resolve_target_dir(args.target_dir)),
            "diagnosis": f"failed to inspect run: {exc}",
            "recoverable": False,
        }

    output = json.dumps(summary, indent=2, ensure_ascii=False) if args.format == "json" else render_markdown(summary)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0 if summary.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
