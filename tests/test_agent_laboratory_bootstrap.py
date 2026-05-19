from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "AI4Math-Auto-Research"
    / "agent-laboratory-workflow"
    / "scripts"
    / "bootstrap_agent_laboratory.py"
)

spec = importlib.util.spec_from_file_location("agent_lab_bootstrap", SCRIPT)
assert spec is not None and spec.loader is not None
agent_lab_bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_lab_bootstrap)


class AgentLaboratoryBootstrapTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_dry_run_generates_agent_laboratory_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "agent-lab"
            result = self.run_script(
                "--target-dir",
                str(target),
                "--env-name",
                "ai4math-agent-lab-test",
                "--dry-run",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["target_dir"], str(target))
            self.assertEqual(payload["env_name"], "ai4math-agent-lab-test")
            self.assertEqual(payload["repo"], "https://github.com/SamuelSchmidgall/AgentLaboratory.git")
            self.assertFalse(target.exists())
            joined = "\n".join(payload["deploy_commands"])
            self.assertIn("git clone", joined)
            self.assertIn("conda create -y -n ai4math-agent-lab-test python=3.12", joined)
            self.assertIn("pip install -r requirements.txt", joined)

    def test_uv_dry_run_generates_virtualenv_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "agent-lab"
            result = self.run_script(
                "--target-dir",
                str(target),
                "--env-manager",
                "uv",
                "--dry-run",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            joined = "\n".join(payload["deploy_commands"])
            self.assertIn("uv venv --python 3.12", joined)
            self.assertIn("uv pip install -r requirements.txt", joined)

    def test_conda_mirror_plan_uses_override_channels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "agent-lab"
            result = self.run_script(
                "--target-dir",
                str(target),
                "--env-name",
                "ai4math-agent-lab-test",
                "--conda-mirror",
                "tuna",
                "--dry-run",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            joined = "\n".join(payload["deploy_commands"])
            self.assertIn("--override-channels", joined)
            self.assertIn("mirrors.tuna.tsinghua.edu.cn", joined)

    def test_conda_uv_installer_plan_installs_into_conda_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "agent-lab"
            result = self.run_script(
                "--target-dir",
                str(target),
                "--env-name",
                "ai4math-agent-lab-test",
                "--installer",
                "uv",
                "--dry-run",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            joined = "\n".join(payload["deploy_commands"])
            self.assertIn("conda create", joined)
            self.assertIn("uv pip install --python /opt/anaconda3/envs/ai4math-agent-lab-test/bin/python", joined)

    def test_check_api_reports_required_keys_without_values(self) -> None:
        result = self.run_script("--check-api", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("OPENAI_API_KEY", payload["api_keys"])
        self.assertIn("LLM_API_KEY", payload["api_keys"])
        self.assertIn("LLM_BASE_URL", payload["endpoint_env"])
        self.assertNotIn("sk-", result.stdout)
        self.assertNotIn("sk-", result.stderr)

    def test_llm_aliases_normalize_to_openai_env(self) -> None:
        args = Namespace(openai_base_url=None, llm_model_id=None, llm_backend=None, lit_review_backend=None)
        env = {
            "LLM_API_KEY": "secret-value",
            "LLM_BASE_URL": "https://example.test/open/api/v1",
            "LLM_MODEL_ID": "ecnu-plus",
        }

        normalized = agent_lab_bootstrap.configure_openai_compatible_env(args, env)

        self.assertEqual(normalized["OPENAI_API_KEY"], "secret-value")
        self.assertEqual(normalized["OPENAI_BASE_URL"], "https://example.test/open/api/v1")
        self.assertEqual(agent_lab_bootstrap.resolve_llm_backend(args, normalized), "ecnu-plus")

    def test_runtime_yaml_uses_model_override_without_persisting_secret(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            source_yaml = target / "config.yaml"
            source_yaml.write_text(
                "\n".join(
                    [
                        "research-topic: smoke",
                        'api-key: "OPENAI-API-KEY-HERE"',
                        'llm-backend: "o3-mini"',
                        'lit-review-backend: "o3-mini"',
                        "compile-latex: true",
                    ]
                ),
                encoding="utf-8",
            )
            args = Namespace(
                target_dir=target,
                experiment_yaml=str(source_yaml),
                research_topic=None,
                llm_backend=None,
                lit_review_backend=None,
                llm_model_id=None,
                openai_base_url=None,
                compile_latex="false",
            )
            env = {"OPENAI_API_KEY": "secret-value", "LLM_MODEL_ID": "ecnu-plus"}

            runtime_yaml = agent_lab_bootstrap.prepare_runtime_yaml(args, env)
            runtime_text = runtime_yaml.read_text(encoding="utf-8")

            self.assertIn("llm-backend: ecnu-plus", runtime_text)
            self.assertIn("lit-review-backend: ecnu-plus", runtime_text)
            self.assertIn("compile-latex: 'false'", runtime_text)
            self.assertNotIn("secret-value", runtime_text)

    def test_runtime_yaml_overrides_research_topic_for_wizard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            source_yaml = target / "config.yaml"
            source_yaml.write_text(
                "\n".join(
                    [
                        "research-topic: old topic",
                        'api-key: "OPENAI-API-KEY-HERE"',
                        'llm-backend: "o3-mini"',
                    ]
                ),
                encoding="utf-8",
            )
            args = Namespace(
                target_dir=target,
                experiment_yaml=str(source_yaml),
                research_topic="new AI4Math research topic",
                llm_backend="ecnu-plus",
                lit_review_backend=None,
                llm_model_id=None,
                openai_base_url=None,
                compile_latex="false",
            )
            env = {"OPENAI_API_KEY": "secret-value"}

            runtime_yaml = agent_lab_bootstrap.prepare_runtime_yaml(args, env)
            runtime_text = runtime_yaml.read_text(encoding="utf-8")

            self.assertIn("research-topic: new AI4Math research topic", runtime_text)
            self.assertNotIn("old topic", runtime_text)

    def test_collect_wizard_config_prompts_for_research_settings(self) -> None:
        answers = iter(["AI4Math research topic", "", "", "", "n", "y", "y"])
        prompts: list[str] = []

        def fake_input(prompt: str) -> str:
            prompts.append(prompt)
            return next(answers)

        args = Namespace(
            research_topic=None,
            openai_base_url=None,
            llm_model_id=None,
            llm_backend=None,
            wizard_mode=None,
            skip_deploy=False,
            skip_core_smoke=False,
            lightweight_imports=False,
            yes=False,
        )
        env = {"LLM_API_KEY": "secret-value"}

        config = agent_lab_bootstrap.collect_wizard_config(args, input_func=fake_input, base_env=env)

        self.assertEqual(config["research_topic"], "AI4Math research topic")
        self.assertEqual(config["model"], "ecnu-plus")
        self.assertEqual(config["mode"], "hybrid")
        self.assertFalse(config["deploy"])
        self.assertTrue(config["core_smoke"])
        self.assertTrue(config["lightweight_imports"])
        self.assertEqual(config["env"]["OPENAI_API_KEY"], "secret-value")
        self.assertTrue(any("Research topic" in prompt for prompt in prompts))

    def test_collect_wizard_config_yes_skips_confirmation_prompts(self) -> None:
        prompts: list[str] = []

        def fake_input(prompt: str) -> str:
            prompts.append(prompt)
            raise AssertionError(f"unexpected prompt: {prompt}")

        args = Namespace(
            research_topic="AI4Math noninteractive topic",
            openai_base_url="https://example.test/open/api/v1",
            llm_model_id="ecnu-plus",
            llm_backend=None,
            wizard_mode="research",
            skip_deploy=False,
            skip_core_smoke=False,
            lightweight_imports=False,
            yes=True,
        )
        env = {"LLM_API_KEY": "secret-value"}

        config = agent_lab_bootstrap.collect_wizard_config(args, input_func=fake_input, base_env=env)

        self.assertEqual(prompts, [])
        self.assertTrue(config["deploy"])
        self.assertTrue(config["core_smoke"])
        self.assertTrue(config["lightweight_imports"])

    def test_collect_wizard_config_codex_native_skips_api_prompts(self) -> None:
        prompts: list[str] = []

        def fake_input(prompt: str) -> str:
            prompts.append(prompt)
            raise AssertionError(f"unexpected prompt: {prompt}")

        args = Namespace(
            research_topic="AI4Math Codex-native topic",
            openai_base_url=None,
            llm_model_id=None,
            llm_backend=None,
            wizard_mode="codex-native",
            skip_deploy=False,
            skip_core_smoke=False,
            lightweight_imports=False,
            yes=True,
        )

        config = agent_lab_bootstrap.collect_wizard_config(args, input_func=fake_input, base_env={})

        self.assertEqual(prompts, [])
        self.assertEqual(config["mode"], "codex-native")
        self.assertEqual(config["model"], "codex-native")
        self.assertFalse(config["deploy"])
        self.assertFalse(config["core_smoke"])

    def test_collect_wizard_config_accepts_legacy_starter_alias(self) -> None:
        args = Namespace(
            research_topic="AI4Math alias topic",
            openai_base_url="https://example.test/open/api/v1",
            llm_model_id="ecnu-plus",
            llm_backend=None,
            wizard_mode="starter",
            skip_deploy=True,
            skip_core_smoke=True,
            lightweight_imports=True,
            yes=True,
        )
        env = {"LLM_API_KEY": "secret-value"}

        config = agent_lab_bootstrap.collect_wizard_config(args, base_env=env)

        self.assertEqual(config["mode"], "research")

    def test_interactive_research_template_includes_literature_review(self) -> None:
        template = (
            ROOT
            / "skills"
            / "AI4Math-Auto-Research"
            / "agent-laboratory-workflow"
            / "templates"
            / "interactive-auto-research.yaml"
        )
        data = yaml.safe_load(template.read_text(encoding="utf-8"))

        self.assertGreaterEqual(data["num-papers-lit-review"], 2)
        literature_notes = "\n".join(data["task-notes"]["literature-review"])
        self.assertIn("Begin with literature review", literature_notes)
        self.assertIn("exactly two papers", literature_notes)
        report_notes = "\n".join(data["task-notes"]["report-writing"])
        self.assertIn("related work", report_notes)

    def test_missing_target_for_verify_fails_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "missing"
            result = self.run_script("--target-dir", str(target), "--verify", "--json")

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("target directory does not exist", payload["errors"][0])

    def test_find_tests_ignores_virtualenv_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".venv" / "lib" / "python3.12" / "site-packages" / "pkg").mkdir(parents=True)
            (target / ".venv" / "lib" / "python3.12" / "site-packages" / "pkg" / "test_vendor.py").write_text(
                "def test_vendor(): pass\n",
                encoding="utf-8",
            )
            (target / "tests").mkdir()
            (target / "tests" / "test_real.py").write_text("def test_real(): pass\n", encoding="utf-8")

            found = {path.relative_to(target).as_posix() for path in agent_lab_bootstrap.find_tests(target)}

            self.assertEqual(found, {"tests/test_real.py"})


if __name__ == "__main__":
    unittest.main()
