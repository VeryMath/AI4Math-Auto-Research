# Agent Laboratory Deployment Notes

Official source: https://github.com/SamuelSchmidgall/AgentLaboratory

Agent Laboratory is the current primary AI4Math Auto-Research platform. The upstream README describes it as an end-to-end workflow with literature review, experimentation, and report writing phases, with optional human feedback and AgentRxiv support.

## Upstream Defaults

- Python: upstream recommends Python 3.12.
- Install:
  - `git clone https://github.com/SamuelSchmidgall/AgentLaboratory.git`
  - `python -m venv venv_agent_lab`
  - `source venv_agent_lab/bin/activate`
  - `pip install -r requirements.txt`
- Optional LaTeX: install `pdflatex` for PDF compilation, or run with `--compile-latex "false"`.
- Example run:
  - `python ai_lab_repo.py --yaml-location "experiment_configs/MATH_agentlab.yaml"`

## AI4Math Deployment Policy

- Keep upstream source under `external/agent-laboratory`, which is ignored by git.
- Use conda environment `ai4math-agent-lab` with Python 3.12 when available.
- Preferred AI4Math command:
  - `python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py --deploy --env-manager conda --conda-mirror tuna --installer uv`
- This keeps the environment as conda while using uv only as the package installer when pip/network stalls.
- Always run local validation before a real experiment.
- Never commit API keys, experiment credentials, generated state saves, or large outputs.
- The helper's model-backed modes (`hybrid`, `core`, `research`, and `full`) require `OPENAI_API_KEY` or its `LLM_API_KEY` alias. The helper maps `LLM_API_KEY` to `OPENAI_API_KEY` before execution.
- `codex-native` uses the active coding agent without an additional model API key.

## Real Experiment Definition

For AI4Math, a real test means:

1. The upstream repository is cloned.
2. Dependencies are installed in an isolated environment.
3. Local verification passes:
   - required files exist
   - `pip check` passes or its conflicts are documented
   - all Python files compile
   - upstream tests run if present
4. A configured Agent Laboratory experiment is launched against `experiment_configs/MATH_agentlab.yaml` or another approved YAML.
5. The result log, generated report, or failure trace is recorded.

## Human Interaction Points

- Before a model-backed experiment or core smoke: if both `OPENAI_API_KEY` and `LLM_API_KEY` are missing, pause and ask the user to provide one through hidden input or the process environment. Configure any additional tool credentials for the services that use them.
- Before code execution: confirm the target experiment YAML and backend.
- After experiment: show logs and generated artifacts before reusing results.

## Troubleshooting Notes

- `CondaHTTPError` on defaults: retry with `--conda-mirror tuna`.
- `IncompleteRead` during conda package download: rerun; conda often reuses partial cache. If repeated, use the narrower tuna main channel.
- `IncompleteRead` or hang during pip install: use `--installer uv`, which installs into the conda Python.
- No upstream tests: still run required-file checks, `pip check`, and `compileall`.
