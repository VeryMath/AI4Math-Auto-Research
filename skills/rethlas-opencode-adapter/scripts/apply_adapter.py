#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from textwrap import dedent


RETHLAS_URL = "https://github.com/frenzymath/Rethlas.git"


GENERATION_RUNNER = r'''#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROBLEM_FILE="${PROBLEM_FILE:-data/example.md}"
MODEL="${MODEL:-gpt-5.5}"
REASONING_EFFORT="${REASONING_EFFORT:-xhigh}"
MAX_ITERATIONS="${MAX_ITERATIONS:-10}"
EXECUTOR="${EXECUTOR:-codex}"

CODEX_BIN="${CODEX_BIN:-codex}"
CODEX_MODEL="${CODEX_MODEL:-$MODEL}"
CODEX_REASONING_EFFORT="${CODEX_REASONING_EFFORT:-$REASONING_EFFORT}"

OPENCODE_BIN="${OPENCODE_BIN:-opencode}"
OPENCODE_AGENT="${OPENCODE_AGENT:-rethlas-generation}"
OPENCODE_NO_SEARCH_AGENT="${OPENCODE_NO_SEARCH_AGENT:-rethlas-generation-no-search}"
OPENCODE_MODEL="${OPENCODE_MODEL:-}"
OPENCODE_VARIANT="${OPENCODE_VARIANT:-}"

if [[ "$PROBLEM_FILE" = /* ]]; then
  echo "PROBLEM_FILE must be relative to agents/generation: $PROBLEM_FILE" >&2
  exit 1
fi

if [[ "$PROBLEM_FILE" == ".." || "$PROBLEM_FILE" == ../* || "$PROBLEM_FILE" == */.. || "$PROBLEM_FILE" == */../* ]]; then
  echo "PROBLEM_FILE must not contain '..': $PROBLEM_FILE" >&2
  exit 1
fi

if [[ "$PROBLEM_FILE" != data/*.md ]]; then
  echo "PROBLEM_FILE must point to a markdown file under data/: $PROBLEM_FILE" >&2
  exit 1
fi

if [[ ! -f "$ROOT_DIR/$PROBLEM_FILE" ]]; then
  echo "Problem file not found: $ROOT_DIR/$PROBLEM_FILE" >&2
  exit 1
fi

if ! [[ "$MAX_ITERATIONS" =~ ^[0-9]+$ ]] || [[ "$MAX_ITERATIONS" -le 0 ]]; then
  echo "MAX_ITERATIONS must be a positive integer: $MAX_ITERATIONS" >&2
  exit 1
fi

case "$EXECUTOR" in
  codex | opencode) ;;
  *)
    echo "EXECUTOR must be one of: codex, opencode" >&2
    exit 1
    ;;
esac

problem_rel="${PROBLEM_FILE#data/}"
problem_rel="${problem_rel%.md}"
problem_name="$(basename "$PROBLEM_FILE" .md)"
ref_dir="data/${problem_rel}.refs"
ref_prompt="Use reference_dir=${ref_dir} if it exists."

prepare_references() {
  local abs_ref_dir="$ROOT_DIR/$ref_dir"
  if [[ ! -d "$abs_ref_dir" ]]; then
    return
  fi

  local pdf_count=0
  while IFS= read -r -d '' pdf; do
    pdf_count=$((pdf_count + 1))
    if ! command -v pdftotext >/dev/null 2>&1; then
      echo "WARNING: found PDF references, but pdftotext is not installed; PDFs will be ignored." >&2
      return
    fi

    local rel_pdf="${pdf#"$abs_ref_dir"/}"
    local txt="$abs_ref_dir/.extracted/${rel_pdf%.pdf}.txt"
    mkdir -p "$(dirname "$txt")"
    if [[ ! -f "$txt" || "$pdf" -nt "$txt" ]]; then
      pdftotext -layout "$pdf" "$txt"
    fi
  done < <(find "$abs_ref_dir" -type f -iname '*.pdf' -not -path "$abs_ref_dir/.extracted/*" -print0)

  if [[ $pdf_count -gt 0 ]]; then
    ref_prompt="Use reference_dir=${ref_dir} if it exists. PDF references have been extracted to ${ref_dir}/.extracted; read those extracted .txt files instead of the PDFs."
  fi
}

extract_session_id() {
  local log_file="$1"

  if [[ "$EXECUTOR" == "codex" ]]; then
    awk -F'session id: ' 'NF > 1 { print $2; exit }' "$log_file"
    return
  fi

  python3 - "$log_file" <<'PY'
import json
import sys

for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    line = line.strip()
    if not line:
        continue
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        continue
    for key in ("sessionID", "sessionId", "session_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            print(value)
            raise SystemExit(0)
PY
}

latest_opencode_session_id() {
  local session_list_file
  session_list_file="$(mktemp)"

  (
    cd "$ROOT_DIR"
    "$OPENCODE_BIN" session list --format json --max-count 1 ||
      "$OPENCODE_BIN" session list --format json
  ) >"$session_list_file" 2>/dev/null || true

  python3 - "$session_list_file" <<'PY'
import json
import sys

raw = open(sys.argv[1], encoding="utf-8", errors="replace").read().strip()
if not raw:
    raise SystemExit(0)

def emit(value):
    if isinstance(value, dict):
        session_id = value.get("id") or value.get("sessionID") or value.get("sessionId")
        if isinstance(session_id, str) and session_id:
            print(session_id)
            raise SystemExit(0)
    if isinstance(value, list):
        for item in value:
            emit(item)

try:
    emit(json.loads(raw))
except json.JSONDecodeError:
    for line in raw.splitlines():
        try:
            emit(json.loads(line))
        except json.JSONDecodeError:
            continue
PY

  rm -f "$session_list_file"
}

command_exists() {
  local bin="$1"
  command -v "$bin" >/dev/null 2>&1 || [[ -x "$bin" ]]
}

executor_version() {
  if [[ "$EXECUTOR" == "codex" ]]; then
    "$CODEX_BIN" --version 2>/dev/null || echo "unknown"
  else
    "$OPENCODE_BIN" --version 2>/dev/null || echo "unknown"
  fi
}

log_and_run() {
  local log_file="$1"
  shift

  {
    printf "command:"
    printf " %q" "$@"
    printf "\n\n"
  } >"$log_file"

  (
    cd "$ROOT_DIR"
    "$@"
  ) >>"$log_file" 2>&1
}

run_codex_first_turn() {
  local prompt="$1"
  local log_file="$2"
  local -a cmd=(
    "$CODEX_BIN" exec
    -C "$ROOT_DIR"
    -m "$CODEX_MODEL"
    --config "model_reasoning_effort=\"$CODEX_REASONING_EFFORT\""
    --dangerously-bypass-approvals-and-sandbox
    "$prompt"
  )
  log_and_run "$log_file" "${cmd[@]}"
}

run_codex_resume_turn() {
  local search_mode="$1"
  local prompt="$2"
  local log_file="$3"
  local codex_web_search="live"

  if [[ "$search_mode" == "disabled" ]]; then
    codex_web_search="disabled"
  fi

  local -a cmd=(
    "$CODEX_BIN" exec resume "$session_id"
    -m "$CODEX_MODEL"
    --config "model_reasoning_effort=\"$CODEX_REASONING_EFFORT\""
    --config "web_search=\"$codex_web_search\""
    --dangerously-bypass-approvals-and-sandbox
    "$prompt"
  )
  log_and_run "$log_file" "${cmd[@]}"
}

run_opencode_turn() {
  local search_mode="$1"
  local prompt="$2"
  local log_file="$3"
  local agent="$OPENCODE_AGENT"

  if [[ "$search_mode" == "disabled" ]]; then
    agent="$OPENCODE_NO_SEARCH_AGENT"
  fi

  local -a cmd=(
    "$OPENCODE_BIN" run
    --dir "$ROOT_DIR"
    --format json
    --auto
  )

  if [[ -n "$session_id" ]]; then
    cmd+=(--session "$session_id")
  fi
  if [[ -n "$agent" ]]; then
    cmd+=(--agent "$agent")
  fi
  if [[ -n "$OPENCODE_MODEL" ]]; then
    cmd+=(--model "$OPENCODE_MODEL")
  fi
  if [[ -n "$OPENCODE_VARIANT" ]]; then
    cmd+=(--variant "$OPENCODE_VARIANT")
  fi

  cmd+=("$prompt")
  log_and_run "$log_file" env \
    OPENCODE_DISABLE_EXTERNAL_SKILLS="${OPENCODE_DISABLE_EXTERNAL_SKILLS:-1}" \
    OPENCODE_DISABLE_CLAUDE_CODE_SKILLS="${OPENCODE_DISABLE_CLAUDE_CODE_SKILLS:-1}" \
    "${cmd[@]}"
}

run_first_turn() {
  local prompt="$1"
  local log_file="$2"

  if [[ "$EXECUTOR" == "codex" ]]; then
    run_codex_first_turn "$prompt" "$log_file"
  else
    run_opencode_turn "enabled" "$prompt" "$log_file"
  fi
}

run_resume_turn() {
  local search_mode="$1"
  local prompt="$2"
  local log_file="$3"

  if [[ "$EXECUTOR" == "codex" ]]; then
    run_codex_resume_turn "$search_mode" "$prompt" "$log_file"
  else
    run_opencode_turn "$search_mode" "$prompt" "$log_file"
  fi
}

format_duration() {
  local total="$1"
  printf "%02d:%02d:%02d" \
    $((total / 3600)) $(((total % 3600) / 60)) $((total % 60))
}

prepare_references

LOG_DIR="${LOG_DIR:-$ROOT_DIR/logs/$problem_rel/iter}"
verified_path="$ROOT_DIR/results/$problem_rel/blueprint_verified.md"
mkdir -p "$LOG_DIR"

if [[ "$EXECUTOR" == "codex" ]]; then
  executor_bin="$CODEX_BIN"
  effective_model="$CODEX_MODEL"
  effective_effort="$CODEX_REASONING_EFFORT"
else
  executor_bin="$OPENCODE_BIN"
  effective_model="${OPENCODE_MODEL:-opencode default}"
  effective_effort="${OPENCODE_VARIANT:-opencode default}"
fi

if ! command_exists "$executor_bin"; then
  echo "Executor binary not found or not executable: $executor_bin" >&2
  exit 1
fi

EXECUTOR_VERSION="$(executor_version)"

echo "========================================"
echo " Executor:   $EXECUTOR"
echo " Binary:     $executor_bin"
echo " Version:    $EXECUTOR_VERSION"
echo " Model:      $effective_model"
echo " Effort:     $effective_effort"
if [[ "$EXECUTOR" == "opencode" ]]; then
  echo " Agent:      $OPENCODE_AGENT"
  echo " No search:  $OPENCODE_NO_SEARCH_AGENT"
fi
echo " Problem:    $PROBLEM_FILE"
echo " Problem ID: $problem_rel"
echo " References: $ref_dir"
echo " Max iters:  $MAX_ITERATIONS"
echo " Logs:       $LOG_DIR"
echo " Stop file:  $verified_path"
echo "========================================"
echo ""

VERIFY_URL="${VERIFY_URL:-http://127.0.0.1:8091/health}"
if ! curl -sf "$VERIFY_URL" >/dev/null 2>&1; then
  echo "WARNING: verification service not reachable at ${VERIFY_URL%%/health*}"
  echo "         The agent may be unable to produce blueprint_verified.md."
  echo "         Start it first if you need verified proofs."
  echo ""
fi

START_EPOCH=$(date +%s)

elapsed_timer() {
  while true; do
    sleep 30
    local now
    now=$(date +%s)
    local secs=$((now - START_EPOCH))
    printf "\r  [elapsed %s] still running..." "$(format_duration "$secs")"
  done
}

elapsed_timer &
TIMER_PID=$!

cleanup_timer() {
  kill "$TIMER_PID" 2>/dev/null || true
  wait "$TIMER_PID" 2>/dev/null || true
}
trap cleanup_timer EXIT

session_id=""

for ((iter = 0; iter < MAX_ITERATIONS; iter += 1)); do
  log_file="$LOG_DIR/${problem_name}_iter_${iter}.md"

  if [[ -f "$verified_path" ]]; then
    echo "Solved problem_id=$problem_rel before iter=$iter"
    break
  fi

  echo "Starting iter=$iter -> $log_file"

  if [[ "$iter" -eq 0 ]]; then
    prompt="Use AGENTS.md exactly to solve the math problem in ${PROBLEM_FILE}. Use problem_id=${problem_rel}. ${ref_prompt}"

    if run_first_turn "$prompt" "$log_file"; then
      executor_rc=0
    else
      executor_rc=$?
    fi

    if [[ "$executor_rc" -ne 0 ]]; then
      echo "$EXECUTOR exited with code $executor_rc at iter=$iter (see $log_file for details)" >&2
      exit "$executor_rc"
    fi

    session_id="$(extract_session_id "$log_file")"
    if [[ -z "$session_id" && "$EXECUTOR" == "opencode" ]]; then
      session_id="$(latest_opencode_session_id || true)"
    fi
    if [[ -z "$session_id" && ! -f "$verified_path" ]]; then
      echo "Could not extract session id from $log_file" >&2
      exit 1
    fi
  elif ((iter % 2 == 1)); then
    no_search_prompt="Please continue. This is a no-search iteration. Do not use search tools, including arXiv theorem search, web search, web fetch, or theorem lookup. Please think deeply by yourself.
"
    if run_resume_turn "disabled" "$no_search_prompt" "$log_file"; then
      executor_rc=0
    else
      executor_rc=$?
    fi

    if [[ "$executor_rc" -ne 0 ]]; then
      echo "$EXECUTOR exited with code $executor_rc at iter=$iter (see $log_file for details)" >&2
      exit "$executor_rc"
    fi
  else
    search_prompt="Please continue. Search tools are enabled for this iteration, including arXiv theorem search and web search when they are useful. Please also think deeply by yourself.
"
    if run_resume_turn "enabled" "$search_prompt" "$log_file"; then
      executor_rc=0
    else
      executor_rc=$?
    fi

    if [[ "$executor_rc" -ne 0 ]]; then
      echo "$EXECUTOR exited with code $executor_rc at iter=$iter (see $log_file for details)" >&2
      exit "$executor_rc"
    fi
  fi

  echo "Finished problem_id=$problem_rel iter=$iter -> $log_file"
done

cleanup_timer
trap - EXIT

END_EPOCH=$(date +%s)
TOTAL=$((END_EPOCH - START_EPOCH))
printf "\n"

if [[ -f "$verified_path" ]]; then
  echo "Solved problem_id=$problem_rel -> $verified_path"
  printf "Total time: %s\n" "$(format_duration "$TOTAL")"
  echo ""
  echo "To view results in the browser, run:"
  echo "  ./site/serve.sh"
  echo "Then open http://localhost:3264"
  exit 0
fi

echo "Reached MAX_ITERATIONS=$MAX_ITERATIONS without verified blueprint for problem_id=$problem_rel" >&2
printf "Total time: %s\n" "$(format_duration "$TOTAL")"
exit 1
'''


VERIFICATION_SERVER = r'''from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


REPO_ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = REPO_ROOT.resolve()
RESULTS_ROOT = WORK_DIR / "results"

VERIFY_EXECUTOR = os.getenv("VERIFY_EXECUTOR", os.getenv("EXECUTOR", "codex")).lower()

CODEX_BIN = os.getenv("CODEX_BIN", "codex")
CODEX_MODEL = os.getenv("CODEX_MODEL", "gpt-5.4")
CODEX_REASONING_EFFORT = os.getenv("CODEX_REASONING_EFFORT", "xhigh")

OPENCODE_BIN = os.getenv("OPENCODE_BIN", "opencode")
OPENCODE_MODEL = os.getenv("OPENCODE_MODEL", "")
OPENCODE_AGENT = os.getenv("OPENCODE_AGENT", "rethlas-verification")
OPENCODE_VARIANT = os.getenv("OPENCODE_VARIANT", "")

VERIFY_TIMEOUT_SECONDS = int(
    os.getenv("VERIFY_TIMEOUT_SECONDS", os.getenv("CODEX_TIMEOUT_SECONDS", "0"))
) or None
VERIFICATION_FILENAMES = ("verification.json", "verificationt.json")

if VERIFY_EXECUTOR not in {"codex", "opencode"}:
    raise ValueError("VERIFY_EXECUTOR must be one of: codex, opencode")


class VerifyRequest(BaseModel):
    statement: str = Field(..., min_length=1)
    proof: str = Field(..., min_length=1)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _statement_hash(statement: str) -> str:
    return hashlib.sha256(statement.encode("utf-8")).hexdigest()[:12]


def generate_run_id(statement: str) -> str:
    return f"{_utc_timestamp()}_{_statement_hash(statement)}"


def _allocate_run_id(statement: str) -> str:
    base = generate_run_id(statement)
    run_id = base
    suffix = 1
    while (RESULTS_ROOT / run_id).exists():
        suffix += 1
        run_id = f"{base}_{suffix}"
    return run_id


def _results_dir(run_id: str) -> Path:
    return RESULTS_ROOT / run_id


def _log_path(run_id: str) -> Path:
    return _results_dir(run_id) / "log.md"


def _verification_path(run_id: str) -> Optional[Path]:
    for filename in VERIFICATION_FILENAMES:
        path = _results_dir(run_id) / filename
        if path.exists():
            return path
    return None


def build_prompt(run_id: str, statement: str, proof: str) -> str:
    return (
        f"Run_id: {run_id}. "
        f"Statement: {statement}. "
        f"Proof:\n{proof}\n\n"
        "Use AGENTS.md to verify the above proof for the statement."
    )


def build_codex_command(run_id: str, statement: str, proof: str) -> List[str]:
    return [
        CODEX_BIN,
        "exec",
        "-C",
        str(WORK_DIR),
        "-m",
        CODEX_MODEL,
        "--config",
        f"model_reasoning_effort={CODEX_REASONING_EFFORT}",
        "--dangerously-bypass-approvals-and-sandbox",
        build_prompt(run_id=run_id, statement=statement, proof=proof),
    ]


def build_opencode_command(run_id: str, statement: str, proof: str) -> List[str]:
    cmd = [
        OPENCODE_BIN,
        "run",
        "--dir",
        str(WORK_DIR),
        "--format",
        "json",
        "--auto",
    ]
    if OPENCODE_AGENT:
        cmd.extend(["--agent", OPENCODE_AGENT])
    if OPENCODE_MODEL:
        cmd.extend(["--model", OPENCODE_MODEL])
    if OPENCODE_VARIANT:
        cmd.extend(["--variant", OPENCODE_VARIANT])
    cmd.append(build_prompt(run_id=run_id, statement=statement, proof=proof))
    return cmd


def build_verification_command(run_id: str, statement: str, proof: str) -> List[str]:
    if VERIFY_EXECUTOR == "codex":
        return build_codex_command(run_id=run_id, statement=statement, proof=proof)
    return build_opencode_command(run_id=run_id, statement=statement, proof=proof)


def build_subprocess_env() -> Dict[str, str]:
    env = os.environ.copy()
    if VERIFY_EXECUTOR == "opencode":
        env.setdefault("OPENCODE_DISABLE_EXTERNAL_SKILLS", "1")
        env.setdefault("OPENCODE_DISABLE_CLAUDE_CODE_SKILLS", "1")
    return env


def run_agent_verification(run_id: str, statement: str, proof: str) -> Dict[str, Any]:
    results_dir = _results_dir(run_id)
    results_dir.mkdir(parents=True, exist_ok=True)
    log_path = _log_path(run_id)
    cmd = build_verification_command(run_id=run_id, statement=statement, proof=proof)

    started_at = datetime.now(timezone.utc).isoformat()
    try:
        with log_path.open("w", encoding="utf-8") as log_handle:
            log_handle.write(f"started_at_utc: {started_at}\n")
            log_handle.write(f"executor: {VERIFY_EXECUTOR}\n")
            log_handle.write(f"command: {shlex.join(cmd)}\n\n")
            log_handle.flush()

            completed = subprocess.run(
                cmd,
                cwd=WORK_DIR,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=VERIFY_TIMEOUT_SECONDS,
                check=False,
                env=build_subprocess_env(),
            )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail=f"{VERIFY_EXECUTOR} verification timed out after {exc.timeout} seconds. See log at {log_path}",
        ) from exc

    verification_path = _verification_path(run_id)
    if completed.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=(
                f"{VERIFY_EXECUTOR} verification failed with exit code {completed.returncode}. "
                f"See log at {log_path}"
            ),
        )

    if verification_path is None:
        expected_primary = _results_dir(run_id) / VERIFICATION_FILENAMES[0]
        raise HTTPException(
            status_code=500,
            detail=(
                f"verification output was not found at {expected_primary}. "
                f"See log at {log_path}"
            ),
        )

    try:
        payload = json.loads(verification_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"verification output at {verification_path} is not valid JSON",
        ) from exc

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=500,
            detail=f"verification output at {verification_path} must be a JSON object",
        )

    return payload


def run_codex_verification(run_id: str, statement: str, proof: str) -> Dict[str, Any]:
    return run_agent_verification(run_id=run_id, statement=statement, proof=proof)


app = FastAPI(title="Verification Agent API", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/verify")
def verify(request: VerifyRequest) -> Dict[str, Any]:
    run_id = _allocate_run_id(request.statement)
    return run_agent_verification(
        run_id=run_id,
        statement=request.statement,
        proof=request.proof,
    )
'''


GENERATION_OPENCODE_JSON = r'''{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "rethlas-generation",
  "instructions": ["AGENTS.md", ".opencode/AGENTS.md"],
  "skills": {
    "paths": [".agents/skills"]
  },
  "mcp": {
    "reasoning_agent": {
      "type": "local",
      "command": ["python3", "./mcp/server.py"],
      "cwd": ".",
      "enabled": true,
      "timeout": 3600000
    }
  },
  "experimental": {
    "mcp_timeout": 3600000
  },
  "tool_output": {
    "max_lines": 4000,
    "max_bytes": 200000
  },
  "compaction": {
    "auto": true,
    "tail_turns": 15
  }
}
'''


GENERATION_OPENCODE_AGENTS = r'''# OpenCode Compatibility

These instructions adapt the shared Rethlas generation workflow in `AGENTS.md` to OpenCode. They define OpenCode-specific tool names and runtime contracts.

## Output Contract

- Treat the output paths from `AGENTS.md` as a hard contract.
- If the user prompt includes `problem_id=<id>`, set `DRAFT_PATH=results/<id>/blueprint.md` and `VERIFIED_PATH=results/<id>/blueprint_verified.md`.
- Preserve category directories in `<id>`. Never flatten `results/<id>/blueprint.md` into `results/<id>.md`, `results/<id>_verified.md`, or similar variants.
- Before claiming the problem is complete, check that `VERIFIED_PATH` exists.

## MCP Tool Names

OpenCode exposes Rethlas MCP tools with the MCP server id as a prefix. When `AGENTS.md` or a skill names a bare MCP tool, call the corresponding OpenCode tool:

| Shared Rethlas tool | OpenCode tool |
| --- | --- |
| `memory_init` | `reasoning_agent_memory_init` |
| `memory_append` | `reasoning_agent_memory_append` |
| `memory_search` | `reasoning_agent_memory_search` |
| `branch_update` | `reasoning_agent_branch_update` |
| `search_arxiv_theorems` | `reasoning_agent_search_arxiv_theorems` |
| `verify_proof_service` | `reasoning_agent_verify_proof_service` |

- MCP tools are native OpenCode tools. Avoid `which memory_init`, `which branch_update`, and similar shell checks when deciding whether MCP is available.
- Avoid calling `mcp.server` functions through `bash` or ad hoc Python as a substitute for native MCP tools. If the prefixed MCP tools are unavailable, report that the OpenCode MCP configuration is not loaded.
- Use the same `problem_id`, memory channels, `DRAFT_PATH`, and `VERIFIED_PATH` that the shared Rethlas workflow requires.

## Subagents

When recursive proving is needed, use OpenCode's `task` tool with `subagent_type="subgoal-prover"` and pass the current decomposition plan and `problem_id`. Subagents must write back to the same memory directory and preserve the same output-path contract.
'''


GENERATION_AGENT = r'''---
description: Rethlas proof generation agent with search enabled.
mode: primary
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit: allow
  bash: allow
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory:
    "*": deny
---

You are the Rethlas proof generation agent. Follow AGENTS.md and .opencode/AGENTS.md exactly.

External search tools are available in this agent when they are useful. Prefer the local MCP theorem search workflow before broad web search, and always persist intermediate artifacts with the memory MCP tools.

When recursive proving is needed, use OpenCode's `task` tool with `subagent_type="subgoal-prover"` to launch a sub-agent for each decomposition plan.
'''


GENERATION_NO_SEARCH_AGENT = r'''---
description: Rethlas proof generation continuation agent for no-search iterations.
mode: primary
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit: allow
  bash: allow
  task: allow
  skill: allow
  webfetch: deny
  websearch: deny
  reasoning_agent_search_arxiv_theorems: deny
  external_directory:
    "*": deny
---

You are the Rethlas proof generation agent in a no-search continuation turn. Follow AGENTS.md and .opencode/AGENTS.md exactly except that this turn must make progress without external retrieval.

Do not use theorem search, web search, web fetch, or any other retrieval tool. Use existing memory, local problem files, previous logs, and deep mathematical reasoning. You may still use memory MCP tools, branch updates, local file operations inside the current working directory, and the verification service when a complete proof candidate is ready.

When recursive proving is needed, use OpenCode's `task` tool with `subagent_type="subgoal-prover"`. The no-search restrictions from this parent session will propagate to sub-agent sessions.
'''


SUBGOAL_AGENT = r'''---
description: Proves all subgoals in a Rethlas subgoal decomposition plan.
mode: subagent
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit: allow
  bash: allow
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory:
    "*": deny
---

You are a Rethlas subgoal prover agent.

Your task is to prove all subgoals in the assigned subgoal decomposition plan. Follow AGENTS.md, .opencode/AGENTS.md, and the relevant `.agents/skills` workflow. Treat the assigned decomposition plan as your starting point.

Write progress, failures, and any successful proof development back into shared memory using the same data-relative `problem_id` as the parent. If you cannot prove every assigned subgoal, summarize exactly which subgoals were proved, which remain open, and what obstruction prevented progress.
'''


VERIFICATION_OPENCODE_JSON = r'''{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "rethlas-verification",
  "instructions": ["AGENTS.md", ".opencode/AGENTS.md"],
  "skills": {
    "paths": [".agents/skills"]
  },
  "mcp": {
    "verification_agent": {
      "type": "local",
      "command": ["python3", "./mcp/server.py"],
      "cwd": ".",
      "enabled": true,
      "timeout": 3600000
    }
  },
  "experimental": {
    "mcp_timeout": 3600000
  },
  "tool_output": {
    "max_lines": 4000,
    "max_bytes": 200000
  },
  "compaction": {
    "auto": true,
    "tail_turns": 15
  }
}
'''


VERIFICATION_OPENCODE_AGENTS = r'''# OpenCode Compatibility

These instructions adapt the shared Rethlas verification workflow in `AGENTS.md` to OpenCode. They define OpenCode-specific tool names and runtime contracts.

## Output Contract

- Use the `run_id` from the verification prompt exactly.
- Write the final verification JSON to `results/{run_id}/verification.json`.
- Return `correct` only when there are no critical errors and no gaps.
- Persist verification memory and intermediate checks through MCP tools before writing the final JSON.

## MCP Tool Names

OpenCode exposes Rethlas MCP tools with the MCP server id as a prefix. When `AGENTS.md` or a skill names a bare MCP tool, call the corresponding OpenCode tool:

| Shared Rethlas tool | OpenCode tool |
| --- | --- |
| `memory_init` | `verification_agent_memory_init` |
| `memory_append` | `verification_agent_memory_append` |
| `memory_query` | `verification_agent_memory_query` |
| `search_arxiv_theorems` | `verification_agent_search_arxiv_theorems` |
| `validate_verification_output` | `verification_agent_validate_verification_output` |
| `write_verification_output` | `verification_agent_write_verification_output` |

- MCP tools are native OpenCode tools. Avoid `which memory_init` and similar shell checks when deciding whether MCP is available.
- Avoid calling `mcp.server` functions through `bash` or ad hoc Python as a substitute for native MCP tools. If the prefixed MCP tools are unavailable, report that the OpenCode MCP configuration is not loaded.
- Use the same `run_id`, memory channels, schema validation, and result path that the shared Rethlas workflow requires.
'''


VERIFICATION_AGENT = r'''---
description: Rethlas proof verification agent.
mode: primary
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit: allow
  bash: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory:
    "*": deny
---

You are the Rethlas proof verification agent. Follow AGENTS.md and .opencode/AGENTS.md exactly.

Use the verification MCP tools to initialize memory, check external theorem references, validate the JSON payload, and write `results/{run_id}/verification.json`. The final verdict must be strict: return `correct` only when there are no critical errors and no gaps.
'''


OPENCODE_GITIGNORE = "node_modules/\npackage.json\npackage-lock.json\n"


FILES = {
    "agents/generation/tests/run_example.sh": (GENERATION_RUNNER, 0o755),
    "agents/verification/api/server.py": (VERIFICATION_SERVER, None),
    "agents/generation/.opencode/opencode.json": (GENERATION_OPENCODE_JSON, None),
    "agents/generation/.opencode/AGENTS.md": (GENERATION_OPENCODE_AGENTS, None),
    "agents/generation/.opencode/agent/rethlas-generation.md": (GENERATION_AGENT, None),
    "agents/generation/.opencode/agent/rethlas-generation-no-search.md": (GENERATION_NO_SEARCH_AGENT, None),
    "agents/generation/.opencode/agent/subgoal-prover.md": (SUBGOAL_AGENT, None),
    "agents/generation/.opencode/.gitignore": (OPENCODE_GITIGNORE, None),
    "agents/verification/.opencode/opencode.json": (VERIFICATION_OPENCODE_JSON, None),
    "agents/verification/.opencode/AGENTS.md": (VERIFICATION_OPENCODE_AGENTS, None),
    "agents/verification/.opencode/agent/rethlas-verification.md": (VERIFICATION_AGENT, None),
    "agents/verification/.opencode/.gitignore": (OPENCODE_GITIGNORE, None),
}


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def git_status(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=repo,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def validate_rethlas_root(repo: Path) -> None:
    required = [
        "agents/generation/AGENTS.md",
        "agents/generation/tests/run_example.sh",
        "agents/generation/mcp/server.py",
        "agents/verification/AGENTS.md",
        "agents/verification/api/server.py",
        "agents/verification/mcp/server.py",
    ]
    missing = [path for path in required if not (repo / path).exists()]
    if missing:
        joined = "\n".join(f"  - {path}" for path in missing)
        raise SystemExit(f"Target does not look like a Rethlas clone. Missing:\n{joined}")


def ensure_repo(target: Path, clone: bool, repo_url: str) -> None:
    if target.exists():
        validate_rethlas_root(target)
    else:
        if not clone:
            raise SystemExit(f"Target does not exist: {target}\nPass --clone to clone Rethlas first.")
        target.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", repo_url, str(target)])
        validate_rethlas_root(target)


def write_file(path: Path, content: str, mode: int | None = None) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        changed = "unchanged"
    else:
        path.write_text(content, encoding="utf-8")
        changed = "written"

    if mode is not None:
        current = path.stat().st_mode
        path.chmod((current & ~0o777) | mode)

    return changed


def apply_adapter(repo: Path) -> None:
    for rel_path, (content, mode) in FILES.items():
        status = write_file(repo / rel_path, content, mode)
        print(f"{status}: {rel_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone or patch FrenzyMath Rethlas so it can run through OpenCode."
    )
    parser.add_argument("--target", required=True, help="Path to the Rethlas clone.")
    parser.add_argument("--clone", action="store_true", help="Clone Rethlas when --target is absent.")
    parser.add_argument("--repo-url", default=RETHLAS_URL, help="Git URL for Rethlas.")
    parser.add_argument("--ref", default=None, help="Optional git ref to checkout before patching.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow patching an existing clone with local git changes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.target).expanduser().resolve()

    if shutil.which("git") is None:
        raise SystemExit("git is required.")

    ensure_repo(target, clone=args.clone, repo_url=args.repo_url)

    dirty = git_status(target)
    if dirty and not args.allow_dirty:
        message = dedent(
            f"""
            The target clone has local changes:
            {dirty.rstrip()}

            Re-run with --allow-dirty only after the user confirms these edits can be overwritten.
            """
        ).strip()
        raise SystemExit(message)

    if args.ref:
        run(["git", "checkout", args.ref], cwd=target)

    apply_adapter(target)

    print()
    print("Adapter applied.")
    print()
    print("Next commands:")
    print(f"  cd {target}/agents/verification")
    print("  python3 -m venv .venv")
    print("  source .venv/bin/activate")
    print("  python -m pip install --upgrade pip")
    print("  python -m pip install -r requirements.txt")
    print("  VERIFY_EXECUTOR=opencode python -m uvicorn api.server:app --host 127.0.0.1 --port 8091")
    print()
    print(f"  cd {target}/agents/generation")
    print("  python3 -m venv .venv")
    print("  source .venv/bin/activate")
    print("  python -m pip install --upgrade pip")
    print("  python -m pip install -r mcp/requirements.txt")
    print("  EXECUTOR=opencode PROBLEM_FILE=data/example.md ./tests/run_example.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
