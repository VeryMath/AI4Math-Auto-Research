from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "agent-laboratory-workflow"
    / "scripts"
    / "prepare_codex_research_workspace.py"
)

spec = importlib.util.spec_from_file_location("codex_research_workspace", SCRIPT)
assert spec is not None and spec.loader is not None
codex_research_workspace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codex_research_workspace)


class CodexResearchWorkspaceTests(unittest.TestCase):
    def test_write_workspace_creates_handoff_and_templates(self) -> None:
        summary = {
            "diagnosis": "incomplete: literature review finished",
            "state_path": "/tmp/Paper0.pkl",
            "research_topic": "PDHG versus Douglas-Rachford",
            "recoverable": True,
            "phase_status": {"literature review": True, "plan formulation": False},
            "recovered": {
                "lit_review_sum": "Recovered PDHG literature.",
                "plan": "",
                "results_code": "",
                "exp_results": "",
                "report": "",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            payload = codex_research_workspace.write_workspace(summary, Path(tmp))

            self.assertTrue(payload["ok"])
            handoff = Path(tmp) / "codex_handoff.md"
            plan = Path(tmp) / "plan.md"
            state = json.loads((Path(tmp) / "research_state.json").read_text(encoding="utf-8"))
            self.assertTrue(handoff.exists())
            self.assertTrue(plan.exists())
            self.assertIn("Codex Takeover Contract", handoff.read_text(encoding="utf-8"))
            self.assertIn("Recovered PDHG literature.", handoff.read_text(encoding="utf-8"))
            self.assertEqual(state["research_topic"], "PDHG versus Douglas-Rachford")

    def test_fallback_summary_supports_codex_native_without_agentlab_state(self) -> None:
        summary = codex_research_workspace.fallback_summary("A numerical optimization topic")

        self.assertFalse(summary["ok"])
        self.assertEqual(summary["stopped_at"], "literature review")
        self.assertIn("codex-native", summary["diagnosis"])
        self.assertEqual(summary["research_topic"], "A numerical optimization topic")


if __name__ == "__main__":
    unittest.main()
