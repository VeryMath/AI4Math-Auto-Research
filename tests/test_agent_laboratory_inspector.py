from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "agent-laboratory-workflow"
    / "scripts"
    / "inspect_agent_laboratory_run.py"
)

spec = importlib.util.spec_from_file_location("agent_lab_inspector", SCRIPT)
assert spec is not None and spec.loader is not None
agent_lab_inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_lab_inspector)


class AgentLaboratoryInspectorTests(unittest.TestCase):
    def test_summarize_workflow_state_marks_literature_only_run_incomplete(self) -> None:
        lit_summary = "Provided here is a literature review on PDHG and Douglas-Rachford."
        fake_agent = SimpleNamespace(
            lit_review=[{"arxiv_id": "1234.5678"}],
            lit_review_sum=lit_summary,
            plan="",
            dataset_code="",
            results_code="",
            exp_results="",
            interpretation="",
            report="",
        )
        workflow = SimpleNamespace(
            research_topic="PDHG versus Douglas-Rachford",
            phase_status={
                "literature review": True,
                "plan formulation": False,
                "data preparation": False,
                "running experiments": False,
                "results interpretation": False,
                "report writing": False,
                "report refinement": False,
            },
            statistics_per_phase={"literature review": {"steps": 10}},
            num_papers_lit_review=2,
            max_steps=6,
            mlesolver_max_steps=1,
            papersolver_max_steps=1,
            reference_papers=["paper one", "paper two"],
            phd=fake_agent,
            postdoc=fake_agent,
            professor=fake_agent,
            ml_engineer=fake_agent,
        )

        summary = agent_lab_inspector.summarize_workflow_state(workflow)

        self.assertFalse(summary["ok"])
        self.assertEqual(summary["stopped_at"], "plan formulation")
        self.assertTrue(summary["recoverable"])
        self.assertIn("literature review finished", summary["diagnosis"])
        self.assertEqual(summary["reference_paper_count"], 2)
        self.assertIn("PDHG", summary["recovered"]["lit_review_sum"])

    def test_render_markdown_includes_recovery_warning(self) -> None:
        summary = {
            "target_dir": "/tmp/agent-laboratory",
            "state_path": "/tmp/agent-laboratory/state_saves/Paper0.pkl",
            "diagnosis": "incomplete: literature review finished",
            "recoverable": True,
            "phase_status": {"literature review": True, "plan formulation": False},
            "recovered": {"lit_review_sum": "PDHG literature summary"},
            "error_evidence": [],
        }

        markdown = agent_lab_inspector.render_markdown(summary)

        self.assertIn("Agent Laboratory Run Diagnosis", markdown)
        self.assertIn("PDHG literature summary", markdown)
        self.assertIn("do not present the run as a finished Auto-Research result", markdown)

    def test_scan_error_evidence_redacts_api_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "run.log"
            fake_key = "sk-" + "testsecret123"
            log.write_text(f"Internal Server Error with token {fake_key}\n", encoding="utf-8")

            evidence = agent_lab_inspector.scan_error_evidence([root])

            self.assertEqual(len(evidence), 1)
            self.assertIn("Internal Server Error", evidence[0]["text"])
            self.assertNotIn(fake_key, evidence[0]["text"])
            self.assertIn("sk-<redacted>", evidence[0]["text"])


if __name__ == "__main__":
    unittest.main()
