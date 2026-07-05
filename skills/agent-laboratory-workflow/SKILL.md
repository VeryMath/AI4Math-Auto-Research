---
name: agent-laboratory-workflow
description: Use when Codex needs to interactively deploy, configure, verify, or launch AI4Math Auto-Research with Agent Laboratory, including API-key handling, user research-topic intake, full local validation, and human review gates.
---

# Agent Laboratory Workflow

## Use When

Use this skill for the AI4Math Auto-Research main platform. It must not stop at "the API works"; it should gather the user's research intent, deploy or update Agent Laboratory, verify the environment, run a real model smoke test, and then launch a bounded research workflow when the user asks to start Auto-Research.

Do not use this skill for generic literature QA; use PaperQA2 or the paper-to-skill module for that.

## Inputs

- Target deployment directory, default `external/agent-laboratory`.
- Conda environment name, default `ai4math-agent-lab`.
- API keys such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `S2_API_KEY`.
- OpenAI-compatible aliases such as `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL_ID`.
- User research topic.
- Run mode: `hybrid`, `core`, `research`, `codex-native`, or `full`.
- Experiment YAML path; research mode defaults to `templates/interactive-auto-research.yaml`.

## Outputs

- Deployment plan or executed deployment.
- Local validation report covering repository files, dependency health, compile checks, and any upstream tests.
- Real model smoke result and, when requested, Agent Laboratory research run result.
- Missing API-key report without printing secret values.
- Runtime YAML path generated under `external/agent-laboratory/.ai4math_runs/`, with API keys redacted.
- Run diagnosis or recovery report when the upstream workflow stops early.
- Codex-native research workspace under `codex_research/` when Agent Laboratory cannot finish or when the user chooses no extra LLM API.

## Workflow

### Default Agent Entry

When the user says "启动 Auto Research", "帮我部署并使用", "交互式输入后开始研究", or equivalent, run the wizard:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --wizard \
  --env-manager conda \
  --conda-mirror tuna \
  --installer uv \
  --lightweight-imports
```

The wizard asks the user for:

- Research topic.
- OpenAI-compatible base URL, default `https://chat.ecnu.edu.cn/open/api/v1`.
- Model ID, default `ecnu-plus`.
- API key, hidden input if not already in `LLM_API_KEY` or `OPENAI_API_KEY`.
- Run mode:
  - `hybrid`: recommended; try bounded Agent Laboratory first, then hand unfinished phases to Codex.
  - `core`: deploy, verify, and test the Agent Laboratory calling chain only.
  - `research`: Agent Laboratory bounded workflow from literature review to report.
  - `codex-native`: no extra model API; create a Codex research workspace and let the coding agent perform the research phases directly.
  - `full`: use the selected upstream/full experiment YAML with larger budget.
- Whether to deploy/update dependencies.
- Whether to run core smoke before launching research.

### Noninteractive Agent Entry

If the user already supplied configuration, a coding agent can launch without extra prompts:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --wizard \
  --wizard-mode hybrid \
  --research-topic "Investigate a lightweight numerical optimization idea for least squares preconditioning" \
  --env-manager conda \
  --conda-mirror tuna \
  --installer uv \
  --llm-model-id ecnu-plus \
  --openai-base-url https://chat.ecnu.edu.cn/open/api/v1 \
  --lightweight-imports \
  --yes \
  --interactive-api
```

If the user explicitly wants to avoid unstable model gateways or has no extra API key, use:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --wizard \
  --wizard-mode codex-native \
  --research-topic "USER_RESEARCH_TOPIC" \
  --codex-workspace-dir codex_research \
  --yes
```

### Manual Steps

Use these when debugging individual stages.

1. Generate a dry-run plan:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py --dry-run
```

2. Deploy and install dependencies:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --deploy \
  --env-manager conda \
  --conda-mirror tuna \
  --installer uv
```

Default policy is conda environment plus uv installer fallback: keep the runtime environment in conda, but use `uv pip --python /opt/anaconda3/envs/<env>/bin/python` when ordinary pip stalls or network reads fail.

3. Run local validation:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py --verify
```

4. Check API-key availability without printing values:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py --check-api
```

For ChatECNU or another OpenAI-compatible gateway, provide secrets only as process environment variables:

```bash
export LLM_API_KEY="<hidden>"
export LLM_BASE_URL="https://chat.ecnu.edu.cn/open/api/v1"
export LLM_MODEL_ID="ecnu-plus"
```

The script maps these to `OPENAI_API_KEY` and `OPENAI_BASE_URL` at runtime without writing the secret into YAML.

5. Run the core smoke. This makes real calls through Agent Laboratory's `query_model`, `PhDStudentAgent`, and generated-code helper route:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --core-smoke \
  --env-manager conda \
  --llm-backend ecnu-plus \
  --lightweight-imports
```

6. Run a research workflow using the interactive template. Research mode is not a mock run: it starts with literature review, adds two papers, then proceeds through plan formulation, data preparation, experiment, results interpretation, and report writing:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --run-experiment \
  --experiment-yaml "$(pwd)/skills/agent-laboratory-workflow/templates/interactive-auto-research.yaml" \
  --research-topic "USER_RESEARCH_TOPIC" \
  --env-manager conda \
  --llm-backend ecnu-plus \
  --compile-latex false \
  --lightweight-imports \
  --experiment-timeout-seconds 600
```

The runner writes a temporary runtime YAML in `external/agent-laboratory/.ai4math_runs/` and keeps API keys out of that file.

7. Run a larger experiment only after `core` or `research` succeeds:

```bash
python skills/agent-laboratory-workflow/scripts/bootstrap_agent_laboratory.py \
  --run-experiment \
  --experiment-yaml experiment_configs/MATH_agentlab.yaml \
  --llm-backend gpt-4o-mini \
  --compile-latex false
```

8. Record generated logs, state saves, reports, and any failure modes in the task notes.

9. If the experiment fails, times out, or produces an unsatisfactory partial result, inspect the run before answering:

```bash
python skills/agent-laboratory-workflow/scripts/inspect_agent_laboratory_run.py \
  --target-dir external/agent-laboratory \
  --format markdown \
  --output auto_research_recovery_report.md
```

Use the diagnosis to report the stopped phase, completed phases, recovered literature review / plan / code / report fragments, and whether the result is a finished research artifact or only a recoverable partial state.

10. Prepare a Codex-native handoff workspace when Agent Laboratory cannot finish or when the user chooses `codex-native`:

```bash
python skills/agent-laboratory-workflow/scripts/prepare_codex_research_workspace.py \
  --target-dir external/agent-laboratory \
  --research-topic "USER_RESEARCH_TOPIC" \
  --output-dir codex_research \
  --json
```

Then Codex must complete the unfinished phases in that workspace: fill `plan.md`, write and run `src/experiment.py`, save outputs under `outputs/`, and write `report.md`.

## Validation

- `--dry-run --json` returns clone, conda, install, verify, and experiment commands without creating the target directory.
- `--verify --json` checks the deployed repository and reports failures as structured JSON.
- Full local validation runs before any real experiment.
- Experiments must not print API keys.
- OpenAI-compatible routing is validated by importing Agent Laboratory's `query_model` and calling the configured `LLM_MODEL_ID`.
- `--wizard` is the preferred user-facing entry. It combines deployment, validation, smoke, and launch.
- `--yes` lets a coding agent use provided values and default confirmations without extra y/n prompts.
- `--research-topic` overrides the template topic in the generated runtime YAML.
- Research mode must preserve the full research arc: literature review -> plan -> data -> experiment -> interpretation -> report. Keep it bounded by paper count, step count, and timeout rather than skipping research phases.
- Hybrid mode must not stop at Agent Laboratory failure. If upstream stops early, create a Codex workspace and finish the remaining research phases directly.

## Failure Modes

- If the target directory is missing, run `--deploy`.
- If conda metadata or package downloads fail, retry with `--conda-mirror tuna`; if pip stalls or hits `IncompleteRead`, rerun deploy with `--installer uv`.
- If conda is unavailable, use `--env-manager uv` as a fallback and record the reason.
- If API keys are missing, pause and ask the user; do not invent or hard-code secrets.
- If a custom model name is not recognized, rerun `--deploy`; the deployment applies the `AI4MATH_OPENAI_COMPATIBLE_PATCH` to Agent Laboratory's model router.
- If LaTeX is unavailable or fails, run with `--compile-latex false`.
- If startup hangs on heavyweight optional imports, rerun smoke with `--lightweight-imports`; full experiments can still use the original upstream import set.
- If the full workflow times out, report the timeout and generated runtime YAML path, then either increase `--experiment-timeout-seconds` or rerun in `research` mode with a smaller topic.
- If backend 500, timeout, or connection errors interrupt the workflow, run `inspect_agent_laboratory_run.py` against the deployment directory. Do not present a literature-only state as a finished Auto-Research result.
- If the diagnosis shows literature review completed but later phases are empty, use the recovered review as seed material and either rerun with a more stable backend / larger timeout or let the coding agent synthesize a plan, executable experiment, and report from the recovered state.
- If the user selects `codex-native`, do not ask for an LLM API key and do not run Agent Laboratory. Create the Codex workspace and perform the research as the current coding agent.
- If the experiment calls generated code, keep it inside the external deployment directory and inspect outputs before reuse.

## Human Interaction Contract

The coding agent should ask the user only for values it cannot infer safely:

- Research topic or research direction.
- API key, hidden input only.
- Whether to run `core`, `research`, or `full`.
- Whether to continue if verification passes but full workflow is likely to be slow or costly.

After those answers, the agent should execute the workflow, debug recoverable environment failures, and return concrete artifacts or a structured failure report.

## References

- `references/agent-laboratory-deployment.md`: deployment notes and source links.
- `scripts/bootstrap_agent_laboratory.py`: deployment, verification, and experiment runner.
