#!/usr/bin/env python3
"""Deploy, verify, and run Agent Laboratory for AI4Math Auto-Research."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_URL = "https://github.com/SamuelSchmidgall/AgentLaboratory.git"
DEFAULT_TARGET = Path("external/agent-laboratory")
DEFAULT_ENV = "ai4math-agent-lab"
DEFAULT_AGENTLAB_YAML = "experiment_configs/MATH_agentlab.yaml"
SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_RESEARCH_YAML = SKILL_DIR / "templates" / "interactive-auto-research.yaml"
PATCH_MARKER = "AI4MATH_OPENAI_COMPATIBLE_PATCH"
REQUIRED_FILES = (
    "ai_lab_repo.py",
    "requirements.txt",
    "experiment_configs/MATH_agentlab.yaml",
)
API_KEYS = ("OPENAI_API_KEY", "LLM_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "S2_API_KEY")
ENDPOINT_ENV = ("OPENAI_BASE_URL", "LLM_BASE_URL", "LLM_MODEL_ID")
CONDA_MIRRORS = {
    "default": (),
    "tuna": (
        "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main",
    ),
}


def _timeout_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def run(
    command: list[str] | str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            env=env,
            shell=isinstance(command, str),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stderr = _timeout_text(exc.stderr)
        stderr += f"\nTIMEOUT: command exceeded {timeout} seconds"
        return subprocess.CompletedProcess(command, 124, _timeout_text(exc.stdout), stderr)


def inspect_failed_run(target_dir: Path) -> dict[str, Any]:
    script = Path(__file__).with_name("inspect_agent_laboratory_run.py")
    result = run(
        [
            sys.executable,
            str(script),
            "--target-dir",
            str(target_dir),
            "--format",
            "json",
            "--no-error-scan",
        ],
        timeout=90,
    )
    if result.stdout.strip():
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            return {
                "ok": False,
                "diagnosis": f"failed to parse run diagnosis JSON: {exc}",
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-2000:],
            }
    return {
        "ok": False,
        "diagnosis": "run diagnosis did not produce JSON output",
        "stderr": result.stderr[-2000:],
    }


def prepare_codex_workspace(args: argparse.Namespace) -> dict[str, Any]:
    script = Path(__file__).with_name("prepare_codex_research_workspace.py")
    command = [
        sys.executable,
        str(script),
        "--research-topic",
        getattr(args, "research_topic", "") or "",
        "--output-dir",
        str(args.codex_workspace_dir),
        "--json",
    ]
    if args.target_dir.exists():
        command.extend(["--target-dir", str(args.target_dir)])
    result = run(command, timeout=90)
    if result.stdout.strip():
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            return {
                "ok": False,
                "diagnosis": f"failed to parse Codex workspace JSON: {exc}",
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-2000:],
            }
    return {
        "ok": False,
        "diagnosis": "Codex workspace preparation did not produce JSON output",
        "stderr": result.stderr[-2000:],
    }


def conda_available() -> bool:
    return shutil.which("conda") is not None


def env_exists(env_name: str) -> bool:
    if not conda_available():
        return False
    result = run(["conda", "env", "list", "--json"])
    if result.returncode != 0:
        return False
    try:
        envs = json.loads(result.stdout).get("envs", [])
    except json.JSONDecodeError:
        return False
    return any(Path(env_path).name == env_name for env_path in envs)


def conda_channel_args(mirror: str) -> list[str]:
    channels = CONDA_MIRRORS.get(mirror)
    if channels is None:
        raise ValueError(f"unknown conda mirror: {mirror}")
    if not channels:
        return []
    args = ["--override-channels"]
    for channel in channels:
        args.extend(["-c", channel])
    return args


def conda_channel_suffix(mirror: str) -> str:
    args = conda_channel_args(mirror)
    return "" if not args else " " + " ".join(args)


def conda_env_python(env_name: str) -> Path:
    return Path("/opt/anaconda3/envs") / env_name / "bin" / "python"


def configure_openai_compatible_env(args: argparse.Namespace | None = None, base_env: dict[str, str] | None = None) -> dict[str, str]:
    """Normalize OpenAI-compatible endpoint aliases without exposing secret values."""
    env = dict(os.environ if base_env is None else base_env)
    if args is not None:
        if args.openai_base_url:
            env["OPENAI_BASE_URL"] = args.openai_base_url
        if args.llm_model_id:
            env["LLM_MODEL_ID"] = args.llm_model_id
    if env.get("LLM_API_KEY") and not env.get("OPENAI_API_KEY"):
        env["OPENAI_API_KEY"] = env["LLM_API_KEY"]
    if env.get("LLM_BASE_URL") and not env.get("OPENAI_BASE_URL"):
        env["OPENAI_BASE_URL"] = env["LLM_BASE_URL"]
    return env


def resolve_llm_backend(args: argparse.Namespace, env: dict[str, str] | None = None) -> str:
    runtime_env = configure_openai_compatible_env(args, env)
    return args.llm_backend or runtime_env.get("LLM_MODEL_ID") or "gpt-4o-mini"


def resolve_lit_review_backend(args: argparse.Namespace, env: dict[str, str] | None = None) -> str:
    return args.lit_review_backend or resolve_llm_backend(args, env)


def ask_text(
    input_func: Any,
    prompt: str,
    default: str | None = None,
    required: bool = False,
) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input_func(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        if not required:
            return ""
        print("This value is required.")


def ask_yes_no(input_func: Any, prompt: str, default: bool = True) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        value = input_func(f"{prompt} [{suffix}]: ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Please answer y or n.")


def collect_wizard_config(
    args: argparse.Namespace,
    input_func: Any = input,
    secret_func: Any = getpass.getpass,
    base_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    env = configure_openai_compatible_env(args, base_env)
    default_topic = "Run a small reproducible AI4Math auto-research experiment with a local numerical example."
    topic = getattr(args, "research_topic", None) or ask_text(input_func, "Research topic", default_topic, required=True)
    mode = getattr(args, "wizard_mode", None) or ask_text(
        input_func,
        "Run mode: hybrid, core, research, codex-native, or full",
        "hybrid",
        required=True,
    )
    if mode == "starter":
        mode = "research"
    if mode not in {"hybrid", "core", "research", "codex-native", "full"}:
        raise ValueError("wizard mode must be one of: hybrid, core, research, codex-native, full")

    if mode == "codex-native":
        return {
            "env": env,
            "research_topic": topic,
            "base_url_set": False,
            "model": "codex-native",
            "mode": mode,
            "deploy": False,
            "core_smoke": False,
            "lightweight_imports": getattr(args, "lightweight_imports", False),
        }

    base_url = (
        getattr(args, "openai_base_url", None)
        or env.get("OPENAI_BASE_URL")
        or ask_text(input_func, "OpenAI-compatible base URL", "https://chat.ecnu.edu.cn/open/api/v1", required=True)
    )
    model = (
        getattr(args, "llm_model_id", None)
        or getattr(args, "llm_backend", None)
        or env.get("LLM_MODEL_ID")
        or ask_text(input_func, "Model ID", "ecnu-plus", required=True)
    )

    if not env.get("OPENAI_API_KEY") and not env.get("LLM_API_KEY"):
        secret = secret_func("LLM_API_KEY / OPENAI_API_KEY (input hidden, not printed): ").strip()
        if secret:
            env["LLM_API_KEY"] = secret

    env["LLM_BASE_URL"] = base_url
    env["OPENAI_BASE_URL"] = base_url
    env["LLM_MODEL_ID"] = model
    if env.get("LLM_API_KEY") and not env.get("OPENAI_API_KEY"):
        env["OPENAI_API_KEY"] = env["LLM_API_KEY"]

    return {
        "env": env,
        "research_topic": topic,
        "base_url_set": bool(base_url),
        "model": model,
        "mode": mode,
        "deploy": not getattr(args, "skip_deploy", False)
        and (getattr(args, "yes", False) or ask_yes_no(input_func, "Deploy/update Agent Laboratory and dependencies", True)),
        "core_smoke": not getattr(args, "skip_core_smoke", False)
        and (getattr(args, "yes", False) or ask_yes_no(input_func, "Run core smoke before starting research", True)),
        "lightweight_imports": getattr(args, "lightweight_imports", False)
        or getattr(args, "yes", False)
        or ask_yes_no(input_func, "Use lightweight imports for faster startup", True),
    }


def patch_agent_laboratory(target_dir: Path) -> dict[str, Any]:
    """Patch upstream Agent Laboratory for OpenAI-compatible endpoints such as ChatECNU."""
    patches: list[dict[str, Any]] = []

    light_imports_path = target_dir / "common_imports_light.py"
    light_imports_text = '''"""Lightweight imports for AI4Math smoke runs.

This keeps Agent Laboratory's smoke path fast while preserving the original
common_imports.py for full experiments.
"""

import argparse
import base64
import collections
import csv
import datetime
import glob
import gzip
import hashlib
import itertools
import json
import logging
import math
import multiprocessing
import os
import pathlib
import pickle
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import time
import uuid
import warnings
import zipfile
from functools import lru_cache, partial
from multiprocessing import Pool

import aiohttp
import h5py
import imageio
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydantic
import requests
import scipy
import seaborn as sns
import sklearn
import yaml
from PIL import Image
from scipy import signal, spatial, stats
from scipy.linalg import eig, svd
from scipy.optimize import minimize
from scipy.spatial.distance import cosine, euclidean
from skimage import color, exposure, filters, io, transform
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.svm import SVC
from statsmodels.api import Logit, OLS
from statsmodels.tsa.stattools import acf, adfuller, pacf
from tqdm import tqdm

tf = None
transformers = None
torch = None
nn = None
optim = None
F = None
DataLoader = None
Dataset = None
random_split = None
'''
    if light_imports_path.exists() and "Lightweight imports for AI4Math smoke runs" in light_imports_path.read_text(encoding="utf-8"):
        patches.append({"file": "common_imports_light.py", "status": "already present"})
    else:
        light_imports_path.write_text(light_imports_text, encoding="utf-8")
        patches.append({"file": "common_imports_light.py", "status": "written"})

    inference_path = target_dir / "inference.py"
    if not inference_path.exists():
        return {"ok": False, "patches": patches, "errors": [f"missing file: {inference_path}"]}
    inference_text = inference_path.read_text(encoding="utf-8")
    if PATCH_MARKER in inference_text:
        patches.append({"file": "inference.py", "status": "already patched"})
    else:
        helper = f'''encoding = tiktoken.get_encoding("cl100k_base")

# {PATCH_MARKER}: support OpenAI-compatible gateways such as ChatECNU.
OPENAI_COMPATIBLE_ALIASES = {{"openai-compatible", "llm-default", "chat-ecnu", "chatecnu"}}
OPENAI_COMPATIBLE_MODELS = {{
    item.strip()
    for item in os.getenv("AI4MATH_OPENAI_COMPATIBLE_MODELS", os.getenv("LLM_MODEL_ID", "ecnu-plus")).split(",")
    if item.strip()
}}


def _openai_base_url():
    return os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL")


def _resolve_openai_compatible_model(model_str):
    if model_str in OPENAI_COMPATIBLE_ALIASES:
        return os.getenv("LLM_MODEL_ID") or "ecnu-plus"
    return model_str


def _is_openai_compatible_model(model_str):
    return model_str in OPENAI_COMPATIBLE_MODELS or model_str in OPENAI_COMPATIBLE_ALIASES


def _openai_compatible_client(openai_api_key=None):
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    kwargs = {{}}
    if api_key:
        kwargs["api_key"] = api_key
    base_url = _openai_base_url()
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)
'''
        inference_text = inference_text.replace('encoding = tiktoken.get_encoding("cl100k_base")\n', helper, 1)
        inference_text = inference_text.replace(
            "    preloaded_api = os.getenv('OPENAI_API_KEY')\n",
            "    preloaded_api = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY')\n",
            1,
        )
        inference_text = inference_text.replace(
            '    for _ in range(tries):\n        try:\n            if model_str == "gpt-4o-mini"',
            '''    if os.getenv("LLM_BASE_URL") and not os.getenv("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = os.getenv("LLM_BASE_URL")
    if os.getenv("LLM_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")
    for _ in range(tries):
        try:
            if _is_openai_compatible_model(model_str):
                model_str = _resolve_openai_compatible_model(model_str)
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                client = _openai_compatible_client(openai_api_key)
                kwargs = {"model": model_str, "messages": messages}
                if temp is not None:
                    kwargs["temperature"] = temp
                completion = client.chat.completions.create(**kwargs)
                answer = completion.choices[0].message.content

            elif model_str == "gpt-4o-mini"''',
            1,
        )
        inference_path.write_text(inference_text, encoding="utf-8")
        patches.append({"file": "inference.py", "status": "patched"})

    inference_text = inference_path.read_text(encoding="utf-8")
    if "AI4MATH_TOKENIZER_FALLBACK_PATCH" in inference_text:
        patches.append({"file": "inference.py", "status": "tokenizer fallback already patched"})
    else:
        inference_text = inference_text.replace(
            "    return sum([costmap_in[_]*TOKENS_IN[_] for _ in TOKENS_IN]) + sum([costmap_out[_]*TOKENS_OUT[_] for _ in TOKENS_OUT])\n",
            "    # AI4MATH_TOKENIZER_FALLBACK_PATCH: unknown OpenAI-compatible models still run; cost is unknown.\n"
            "    return sum([costmap_in.get(_, 0)*TOKENS_IN[_] for _ in TOKENS_IN]) + sum([costmap_out.get(_, 0)*TOKENS_OUT[_] for _ in TOKENS_OUT])\n",
            1,
        )
        inference_text = inference_text.replace(
            "                    encoding = tiktoken.encoding_for_model(model_str)\n",
            "                    try:\n"
            "                        encoding = tiktoken.encoding_for_model(model_str)\n"
            "                    except KeyError:\n"
            "                        encoding = tiktoken.get_encoding(\"cl100k_base\")\n",
            1,
        )
        inference_path.write_text(inference_text, encoding="utf-8")
        patches.append({"file": "inference.py", "status": "tokenizer fallback patched"})

    utils_path = target_dir / "utils.py"
    if not utils_path.exists():
        return {"ok": False, "patches": patches, "errors": [f"missing file: {utils_path}"]}
    utils_text = utils_path.read_text(encoding="utf-8")
    if PATCH_MARKER in utils_text:
        patches.append({"file": "utils.py", "status": "already patched"})
    else:
        utils_helper = f'''from huggingface_hub import InferenceClient

# {PATCH_MARKER}: let generated helper calls use OpenAI-compatible gateways.
def _ai4math_openai_client(api_key=None):
    resolved_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    kwargs = {{}}
    if resolved_key:
        kwargs["api_key"] = resolved_key
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _ai4math_openai_model(default_model):
    return os.getenv("LLM_MODEL_ID") or default_model
'''
        utils_text = utils_text.replace("from huggingface_hub import InferenceClient\n", utils_helper, 1)
        utils_text = utils_text.replace(
            '        openai_api_key = api_key\n        openai.api_key = openai_api_key\n        os.environ["OPENAI_API_KEY"] = openai_api_key\n',
            '        openai_api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")\n        if openai_api_key:\n            openai.api_key = openai_api_key\n            os.environ["OPENAI_API_KEY"] = openai_api_key\n        if os.getenv("LLM_BASE_URL") and not os.getenv("OPENAI_BASE_URL"):\n            os.environ["OPENAI_BASE_URL"] = os.getenv("LLM_BASE_URL")\n',
        )
        utils_text = utils_text.replace(
            '        client = OpenAI()\n        response = client.chat.completions.create(\n            model="gpt-4o-mini", messages=messages, temperature=temperature).choices[0].message.content.strip()\n',
            '        client = _ai4math_openai_client(openai_api_key)\n        response = client.chat.completions.create(\n            model=_ai4math_openai_model("gpt-4o-mini"), messages=messages, temperature=temperature).choices[0].message.content.strip()\n',
            1,
        )
        utils_text = utils_text.replace(
            '        client = OpenAI()\n        response = client.chat.completions.create(\n            model="gpt-4o", messages=messages, temperature=temperature).choices[0].message.content.strip()\n',
            '        client = _ai4math_openai_client(openai_api_key)\n        response = client.chat.completions.create(\n            model=_ai4math_openai_model("gpt-4o"), messages=messages, temperature=temperature).choices[0].message.content.strip()\n',
            1,
        )
        utils_path.write_text(utils_text, encoding="utf-8")
        patches.append({"file": "utils.py", "status": "patched"})

    common_imports_path = target_dir / "common_imports.py"
    if not common_imports_path.exists():
        return {"ok": False, "patches": patches, "errors": [f"missing file: {common_imports_path}"]}
    common_imports_text = common_imports_path.read_text(encoding="utf-8")
    if "AI4MATH_OPTIONAL_TENSORFLOW_PATCH" in common_imports_text:
        patches.append({"file": "common_imports.py", "status": "already patched"})
    else:
        common_imports_text = common_imports_text.replace(
            "import tensorflow as tf\n#import keras\n",
            '''# AI4MATH_OPTIONAL_TENSORFLOW_PATCH: TensorFlow is optional for lightweight smoke runs.
try:
    import tensorflow as tf
except ImportError:
    tf = None
#import keras
''',
            1,
        )
        common_imports_path.write_text(common_imports_text, encoding="utf-8")
        patches.append({"file": "common_imports.py", "status": "patched"})

    ai_lab_path = target_dir / "ai_lab_repo.py"
    if not ai_lab_path.exists():
        return {"ok": False, "patches": patches, "errors": [f"missing file: {ai_lab_path}"]}
    ai_lab_text = ai_lab_path.read_text(encoding="utf-8")
    if PATCH_MARKER in ai_lab_text:
        patches.append({"file": "ai_lab_repo.py", "status": "already patched"})
    else:
        ai_lab_helper = f'''os.environ["TOKENIZERS_PARALLELISM"] = "false"

# {PATCH_MARKER}: accept LLM_* aliases used by AI4Math deployment skills.
def ai4math_configure_openai_compatible_env():
    if os.getenv("LLM_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")
    if os.getenv("LLM_BASE_URL") and not os.getenv("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = os.getenv("LLM_BASE_URL")
'''
        ai_lab_text = ai_lab_text.replace('os.environ["TOKENIZERS_PARALLELISM"] = "false"\n', ai_lab_helper, 1)
        ai_lab_text = ai_lab_text.replace(
            "    api_key = (os.getenv('OPENAI_API_KEY') or args.api_key) if (hasattr(args, 'api_key') or os.getenv('OPENAI_API_KEY')) else None\n",
            "    ai4math_configure_openai_compatible_env()\n    api_key = (os.getenv('OPENAI_API_KEY') or args.api_key) if (hasattr(args, 'api_key') or os.getenv('OPENAI_API_KEY')) else None\n",
            1,
        )
        ai_lab_path.write_text(ai_lab_text, encoding="utf-8")
        patches.append({"file": "ai_lab_repo.py", "status": "patched"})

    if "AI4MATH_MAX_STEPS_PATCH" in ai_lab_text:
        patches.append({"file": "ai_lab_repo.py", "status": "max-steps already patched"})
    else:
        ai_lab_text = ai_lab_path.read_text(encoding="utf-8")
        ai_lab_text = ai_lab_text.replace(
            "    if 'mlesolver-max-steps' in agentlab_data: parser.mlesolver_max_steps = agentlab_data[\"mlesolver-max-steps\"]\n",
            "    # AI4MATH_MAX_STEPS_PATCH: expose the workflow turn budget for smoke tests.\n"
            "    if 'max-steps' in agentlab_data: parser.max_steps = agentlab_data[\"max-steps\"]\n"
            "    else: parser.max_steps = 6\n"
            "    if 'mlesolver-max-steps' in agentlab_data: parser.mlesolver_max_steps = agentlab_data[\"mlesolver-max-steps\"]\n",
            1,
        )
        ai_lab_text = ai_lab_text.replace(
            "    try: mlesolver_max_steps = int(args.mlesolver_max_steps.lower()) if type(args.mlesolver_max_steps) == str else args.mlesolver_max_steps\n"
            "    except Exception: raise Exception(\"args.mlesolver_max_steps must be a valid integer!\")\n",
            "    try: mlesolver_max_steps = int(args.mlesolver_max_steps.lower()) if type(args.mlesolver_max_steps) == str else args.mlesolver_max_steps\n"
            "    except Exception: raise Exception(\"args.mlesolver_max_steps must be a valid integer!\")\n"
            "    try: max_steps = int(args.max_steps.lower()) if type(args.max_steps) == str else args.max_steps\n"
            "    except Exception: raise Exception(\"args.max_steps must be a valid integer!\")\n",
            1,
        )
        ai_lab_text = ai_lab_text.replace(
            "                    notes=task_notes_LLM,\n                    agent_model_backbone=agent_models,\n",
            "                    notes=task_notes_LLM,\n                    max_steps=max_steps,\n                    agent_model_backbone=agent_models,\n",
        )
        ai_lab_path.write_text(ai_lab_text, encoding="utf-8")
        patches.append({"file": "ai_lab_repo.py", "status": "max-steps patched"})

    ai_lab_text = ai_lab_path.read_text(encoding="utf-8")
    if "AI4MATH_LAZY_APP_PATCH" in ai_lab_text:
        patches.append({"file": "ai_lab_repo.py", "status": "lazy app already patched"})
    else:
        lazy_app_helper = '''# AI4MATH_LAZY_APP_PATCH: the web UI imports optional Flask dependencies; load it only for AgentRxiv.
app = None
update_papers_from_uploads = None
run_app = None


def ai4math_ensure_app_loaded():
    global app, update_papers_from_uploads, run_app
    if app is None:
        from app import app as loaded_app, update_papers_from_uploads as loaded_update, run_app as loaded_run
        app = loaded_app
        update_papers_from_uploads = loaded_update
        run_app = loaded_run

'''
        ai_lab_text = ai_lab_text.replace("from app import *\n", lazy_app_helper, 1)
        ai_lab_text = ai_lab_text.replace(
            "class AgentRxiv:\n    def __init__(self, lab_index=0):\n        self.lab_index = lab_index\n",
            "class AgentRxiv:\n    def __init__(self, lab_index=0):\n        ai4math_ensure_app_loaded()\n        self.lab_index = lab_index\n",
            1,
        )
        ai_lab_path.write_text(ai_lab_text, encoding="utf-8")
        patches.append({"file": "ai_lab_repo.py", "status": "lazy app patched"})

    common_import_block = (
        "# AI4MATH_LIGHTWEIGHT_IMPORTS_PATCH\n"
        "import os\n"
        "if os.getenv(\"AI4MATH_LIGHTWEIGHT_IMPORTS\") == \"1\":\n"
        "    from common_imports_light import *\n"
        "else:\n"
        "    from common_imports import *\n"
    )
    for relative in ("ai_lab_repo.py", "mlesolver.py", "papersolver.py"):
        path = target_dir / relative
        text = path.read_text(encoding="utf-8")
        if "AI4MATH_LIGHTWEIGHT_IMPORTS_PATCH" in text:
            patches.append({"file": relative, "status": "lightweight imports already patched"})
            continue
        text = text.replace("from common_imports import *\n", common_import_block, 1)
        path.write_text(text, encoding="utf-8")
        patches.append({"file": relative, "status": "lightweight imports patched"})

    return {"ok": True, "patches": patches}


def deploy_commands(
    target_dir: Path,
    env_name: str,
    env_manager: str,
    conda_mirror: str = "default",
    installer: str = "pip",
) -> list[str]:
    if env_manager == "uv":
        return [
            f"git clone {REPO_URL} {target_dir}",
            f"patch Agent Laboratory with {PATCH_MARKER}",
            f"uv venv --python 3.12 {target_dir / '.venv'}",
            f"uv pip install --python {target_dir / '.venv' / 'bin' / 'python'} --upgrade pip",
            f"cd {target_dir} && source .venv/bin/activate && uv pip install -r requirements.txt",
        ]
    if installer == "uv":
        python = conda_env_python(env_name)
        return [
            f"git clone {REPO_URL} {target_dir}",
            f"patch Agent Laboratory with {PATCH_MARKER}",
            f"conda create -y -n {env_name} python=3.12{conda_channel_suffix(conda_mirror)}",
            f"uv pip install --python {python} --upgrade pip",
            f"uv pip install --python {python} -r {target_dir / 'requirements.txt'}",
        ]
    return [
        f"git clone {REPO_URL} {target_dir}",
        f"patch Agent Laboratory with {PATCH_MARKER}",
        f"conda create -y -n {env_name} python=3.12{conda_channel_suffix(conda_mirror)}",
        f"conda run -n {env_name} python -m pip install --upgrade pip",
        f"cd {target_dir} && conda run -n {env_name} python -m pip install -r requirements.txt",
    ]


def python_command(target_dir: Path, env_name: str, env_manager: str) -> list[str]:
    if env_manager == "uv":
        return [str(target_dir / ".venv" / "bin" / "python")]
    return ["conda", "run", "-n", env_name, "python"]


def experiment_command(target_dir: Path, env_name: str, env_manager: str, yaml_path: str, llm_backend: str, compile_latex: str) -> str:
    base = " ".join(python_command(target_dir, env_name, env_manager))
    return (
        f"write runtime YAML with llm-backend={llm_backend!r}, compile-latex={compile_latex!r}; "
        f"{base} ai_lab_repo.py --yaml-location <runtime-yaml-derived-from-{yaml_path}>"
    )


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "repo": REPO_URL,
        "target_dir": str(args.target_dir),
        "env_name": args.env_name,
        "env_manager": args.env_manager,
        "conda_mirror": args.conda_mirror,
        "installer": args.installer,
        "deploy_commands": deploy_commands(
            args.target_dir,
            args.env_name,
            args.env_manager,
            args.conda_mirror,
            args.installer,
        ),
        "verify_commands": [
            f"{' '.join(python_command(args.target_dir, args.env_name, args.env_manager))} -m pip check",
            f"{' '.join(python_command(args.target_dir, args.env_name, args.env_manager))} -m compileall -q {args.target_dir}",
            "pytest if upstream tests are present",
        ],
        "experiment_command": experiment_command(
            args.target_dir,
            args.env_name,
            args.env_manager,
            args.experiment_yaml,
            resolve_llm_backend(args),
            args.compile_latex,
        ),
        "required_api_keys": list(API_KEYS),
        "endpoint_env": list(ENDPOINT_ENV),
        "lightweight_imports": args.lightweight_imports,
        "dry_run": args.dry_run,
    }


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def check_api(as_json: bool, interactive: bool = False) -> int:
    configure_openai_compatible_env()
    api_status = {name: bool(os.environ.get(name)) for name in API_KEYS}
    endpoint_status = {name: bool(os.environ.get(name)) for name in ENDPOINT_ENV}
    if interactive and not api_status["OPENAI_API_KEY"]:
        secret = getpass.getpass("OPENAI_API_KEY (input hidden, not printed): ").strip()
        if secret:
            os.environ["OPENAI_API_KEY"] = secret
            api_status["OPENAI_API_KEY"] = True
    emit({"api_keys": api_status, "endpoint_env": endpoint_status, "ok": any(api_status.values())}, as_json)
    return 0


def deploy(target_dir: Path, env_name: str, env_manager: str, conda_mirror: str, installer: str) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    if not target_dir.exists():
        result = run(["git", "clone", REPO_URL, str(target_dir)])
        results.append({"step": "git clone", "returncode": result.returncode, "stderr": result.stderr[-2000:]})
        if result.returncode != 0:
            return {"ok": False, "results": results}
    else:
        results.append({"step": "git clone", "returncode": 0, "stderr": "target exists; skipped clone"})

    patch_result = patch_agent_laboratory(target_dir)
    results.append({"step": "patch openai compatible", "returncode": 0 if patch_result.get("ok") else 1, "stderr": json.dumps(patch_result, ensure_ascii=False)})
    if not patch_result.get("ok"):
        return {"ok": False, "results": results}

    if env_manager == "uv":
        if shutil.which("uv") is None:
            return {"ok": False, "results": results, "errors": ["uv is not available"]}
        venv_python = target_dir / ".venv" / "bin" / "python"
        if not venv_python.exists():
            result = run(["uv", "venv", "--python", "3.12", str(target_dir / ".venv")])
            results.append({"step": "uv venv", "returncode": result.returncode, "stderr": result.stderr[-2000:]})
            if result.returncode != 0:
                return {"ok": False, "results": results}
        else:
            results.append({"step": "uv venv", "returncode": 0, "stderr": "virtualenv exists; skipped create"})
        for step_name, command in (
            ("pip upgrade", ["uv", "pip", "install", "--python", str(venv_python), "--upgrade", "pip"]),
            (
                "pip install requirements",
                ["uv", "pip", "install", "--python", str(venv_python), "-r", str(target_dir / "requirements.txt")],
            ),
        ):
            result = run(command)
            results.append({"step": step_name, "returncode": result.returncode, "stderr": result.stderr[-2000:]})
            if result.returncode != 0:
                return {"ok": False, "results": results}
        return {"ok": True, "results": results}

    if not conda_available():
        return {"ok": False, "results": results, "errors": ["conda is not available"]}

    if not env_exists(env_name):
        create_command = ["conda", "create", "-y", "-n", env_name, "python=3.12"]
        create_command.extend(conda_channel_args(conda_mirror))
        result = run(create_command)
        results.append({"step": "conda create", "returncode": result.returncode, "stderr": result.stderr[-2000:]})
        if result.returncode != 0 and conda_mirror == "default":
            mirror_command = ["conda", "create", "-y", "-n", env_name, "python=3.12"]
            mirror_command.extend(conda_channel_args("tuna"))
            mirror_result = run(mirror_command)
            results.append(
                {
                    "step": "conda create retry with tuna mirror",
                    "returncode": mirror_result.returncode,
                    "stderr": mirror_result.stderr[-2000:],
                }
            )
            result = mirror_result
        if result.returncode != 0:
            return {"ok": False, "results": results}
    else:
        results.append({"step": "conda create", "returncode": 0, "stderr": "environment exists; skipped create"})

    if installer == "uv":
        if shutil.which("uv") is None:
            return {"ok": False, "results": results, "errors": ["uv is not available"]}
        python = conda_env_python(env_name)
        install_steps = (
            ("pip upgrade", ["uv", "pip", "install", "--python", str(python), "--upgrade", "pip"]),
            ("pip install requirements", ["uv", "pip", "install", "--python", str(python), "-r", str(target_dir / "requirements.txt")]),
        )
    else:
        install_steps = (
            ("pip upgrade", ["conda", "run", "-n", env_name, "python", "-m", "pip", "install", "--upgrade", "pip"]),
            (
                "pip install requirements",
                ["conda", "run", "-n", env_name, "python", "-m", "pip", "install", "-r", str(target_dir / "requirements.txt")],
            ),
        )

    for step_name, command in install_steps:
        result = run(command)
        results.append({"step": step_name, "returncode": result.returncode, "stderr": result.stderr[-2000:]})
        if result.returncode != 0:
            return {"ok": False, "results": results}

    return {"ok": True, "results": results}


def find_tests(target_dir: Path) -> list[Path]:
    candidates = []
    for pattern in ("test_*.py", "*_test.py"):
        candidates.extend(target_dir.rglob(pattern))
    ignored_parts = {"venv_agent_lab", ".venv", ".git", "__pycache__"}
    return [path for path in candidates if not ignored_parts.intersection(path.parts)]


def verify(target_dir: Path, env_name: str, env_manager: str) -> tuple[int, dict[str, Any]]:
    target_dir = target_dir.resolve()
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    if not target_dir.exists():
        return 2, {"ok": False, "errors": [f"target directory does not exist: {target_dir}"], "checks": checks}

    for relative in REQUIRED_FILES:
        exists = (target_dir / relative).exists()
        checks.append({"check": f"required file {relative}", "ok": exists})
        if not exists:
            errors.append(f"missing required file: {relative}")

    if env_manager == "uv":
        python = target_dir / ".venv" / "bin" / "python"
        if not python.exists():
            errors.append(f"uv virtualenv python does not exist: {python}")
            return 1, {"ok": False, "errors": errors, "checks": checks}

        pip_check = run([str(python), "-m", "pip", "check"])
        checks.append(
            {
                "check": "pip check",
                "ok": pip_check.returncode == 0,
                "stdout": pip_check.stdout[-2000:],
                "stderr": pip_check.stderr[-2000:],
            }
        )
        if pip_check.returncode != 0:
            errors.append("pip check failed")

        compile_check = run([str(python), "-m", "compileall", "-q", str(target_dir)])
        checks.append(
            {
                "check": "compileall",
                "ok": compile_check.returncode == 0,
                "stdout": compile_check.stdout[-2000:],
                "stderr": compile_check.stderr[-2000:],
            }
        )
        if compile_check.returncode != 0:
            errors.append("compileall failed")

        tests = find_tests(target_dir)
        if tests:
            pytest_check = run([str(python), "-m", "pytest", "-q"], cwd=target_dir)
            checks.append(
                {
                    "check": "upstream pytest",
                    "ok": pytest_check.returncode == 0,
                    "test_count_hint": len(tests),
                    "stdout": pytest_check.stdout[-4000:],
                    "stderr": pytest_check.stderr[-4000:],
                }
            )
            if pytest_check.returncode != 0:
                errors.append("upstream pytest failed")
        else:
            checks.append({"check": "upstream pytest", "ok": True, "stdout": "no upstream tests found"})

    elif not conda_available():
        errors.append("conda is not available")
    elif not env_exists(env_name):
        errors.append(f"conda environment does not exist: {env_name}")
    else:
        pip_check = run(["conda", "run", "-n", env_name, "python", "-m", "pip", "check"])
        checks.append(
            {
                "check": "pip check",
                "ok": pip_check.returncode == 0,
                "stdout": pip_check.stdout[-2000:],
                "stderr": pip_check.stderr[-2000:],
            }
        )
        if pip_check.returncode != 0:
            errors.append("pip check failed")

        compile_check = run(["conda", "run", "-n", env_name, "python", "-m", "compileall", "-q", str(target_dir)])
        checks.append(
            {
                "check": "compileall",
                "ok": compile_check.returncode == 0,
                "stdout": compile_check.stdout[-2000:],
                "stderr": compile_check.stderr[-2000:],
            }
        )
        if compile_check.returncode != 0:
            errors.append("compileall failed")

        tests = find_tests(target_dir)
        if tests:
            pytest_check = run(["conda", "run", "-n", env_name, "python", "-m", "pytest", "-q"], cwd=target_dir)
            checks.append(
                {
                    "check": "upstream pytest",
                    "ok": pytest_check.returncode == 0,
                    "test_count_hint": len(tests),
                    "stdout": pytest_check.stdout[-4000:],
                    "stderr": pytest_check.stderr[-4000:],
                }
            )
            if pytest_check.returncode != 0:
                errors.append("upstream pytest failed")
        else:
            checks.append({"check": "upstream pytest", "ok": True, "stdout": "no upstream tests found"})

    return (0 if not errors else 1), {"ok": not errors, "errors": errors, "checks": checks}


def prepare_runtime_yaml(args: argparse.Namespace, env: dict[str, str]) -> Path:
    yaml_source = Path(args.experiment_yaml)
    if not yaml_source.is_absolute():
        yaml_source = args.target_dir / yaml_source
    data = yaml.safe_load(yaml_source.read_text(encoding="utf-8")) or {}
    llm_backend = resolve_llm_backend(args, env)
    data["llm-backend"] = llm_backend
    data["lit-review-backend"] = resolve_lit_review_backend(args, env)
    data["compile-latex"] = args.compile_latex
    if getattr(args, "research_topic", None):
        data["research-topic"] = args.research_topic
    if "api-key" in data and env.get("OPENAI_API_KEY"):
        data["api-key"] = "OPENAI-API-KEY-HERE"

    runtime_dir = args.target_dir.resolve() / ".ai4math_runs"
    runtime_dir.mkdir(exist_ok=True)
    runtime_yaml = runtime_dir / f"{yaml_source.stem}.runtime.yaml"
    runtime_yaml.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return runtime_yaml


def run_experiment(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    env = configure_openai_compatible_env(args)
    env["PYTHONUNBUFFERED"] = "1"
    if args.lightweight_imports:
        env["AI4MATH_LIGHTWEIGHT_IMPORTS"] = "1"
    if not env.get("OPENAI_API_KEY"):
        if args.interactive_api:
            secret = getpass.getpass("OPENAI_API_KEY (input hidden, not printed): ").strip()
            if secret:
                env["OPENAI_API_KEY"] = secret
        if not env.get("OPENAI_API_KEY"):
            return 3, {"ok": False, "errors": ["OPENAI_API_KEY or LLM_API_KEY is required for a real experiment"]}

    code, verification = verify(args.target_dir, args.env_name, args.env_manager)
    if code != 0:
        return code, {"ok": False, "errors": ["verification failed before experiment"], "verification": verification}

    patch_result = patch_agent_laboratory(args.target_dir)
    if not patch_result.get("ok"):
        return 1, {"ok": False, "errors": ["failed to apply OpenAI-compatible patch"], "patch": patch_result}

    runtime_yaml = prepare_runtime_yaml(args, env)
    command = [
        *python_command(args.target_dir, args.env_name, args.env_manager),
        "-u",
        "ai_lab_repo.py",
        "--yaml-location",
        str(runtime_yaml),
    ]
    result = run(command, cwd=args.target_dir, env=env, timeout=args.experiment_timeout_seconds)
    payload: dict[str, Any] = {
        "ok": result.returncode == 0,
        "command": " ".join(command),
        "runtime_yaml": str(runtime_yaml),
        "llm_backend": resolve_llm_backend(args, env),
        "lightweight_imports": args.lightweight_imports,
        "stdout": result.stdout[-8000:],
        "stderr": result.stderr[-8000:],
    }
    if result.returncode != 0:
        payload["run_diagnosis"] = inspect_failed_run(args.target_dir)
        payload["codex_workspace"] = prepare_codex_workspace(args)
    return result.returncode, payload


def run_core_smoke(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    env = configure_openai_compatible_env(args)
    env["PYTHONUNBUFFERED"] = "1"
    if args.lightweight_imports:
        env["AI4MATH_LIGHTWEIGHT_IMPORTS"] = "1"
    if not env.get("OPENAI_API_KEY"):
        if args.interactive_api:
            secret = getpass.getpass("OPENAI_API_KEY (input hidden, not printed): ").strip()
            if secret:
                env["OPENAI_API_KEY"] = secret
        if not env.get("OPENAI_API_KEY"):
            return 3, {"ok": False, "errors": ["OPENAI_API_KEY or LLM_API_KEY is required for core smoke"]}

    code, verification = verify(args.target_dir, args.env_name, args.env_manager)
    if code != 0:
        return code, {"ok": False, "errors": ["verification failed before core smoke"], "verification": verification}

    patch_result = patch_agent_laboratory(args.target_dir)
    if not patch_result.get("ok"):
        return 1, {"ok": False, "errors": ["failed to apply OpenAI-compatible patch"], "patch": patch_result}

    env["AI4MATH_SMOKE_MODEL"] = resolve_llm_backend(args, env)
    smoke_code = r'''
import json
import os

from agents import PhDStudentAgent
from inference import query_model
from utils import query_gpt4omini

model = os.environ["AI4MATH_SMOKE_MODEL"]
query_answer = query_model(
    model_str=model,
    system_prompt="You are running a deployment smoke test.",
    prompt="Reply exactly: AI4MATH_QUERY_OK",
    tries=1,
    timeout=1,
    print_cost=False,
)
agent = PhDStudentAgent(model=model, max_steps=3, openai_api_key=os.environ["OPENAI_API_KEY"])
agent_answer = agent.override_inference("Reply exactly: AI4MATH_AGENT_OK", temp=0.0)
helper_answer = query_gpt4omini(
    prompt="Reply exactly: AI4MATH_HELPER_OK",
    system="You are running a deployment smoke test.",
    api_key=os.environ["OPENAI_API_KEY"],
    attempt=10,
    temperature=0.0,
)
print(json.dumps({
    "query_model_ok": "AI4MATH_QUERY_OK" in query_answer,
    "agent_ok": "AI4MATH_AGENT_OK" in agent_answer,
    "helper_ok": "AI4MATH_HELPER_OK" in helper_answer,
    "model": model,
    "chars": {
        "query_model": len(query_answer or ""),
        "agent": len(agent_answer or ""),
        "helper": len(helper_answer or ""),
    },
}, ensure_ascii=False))
'''
    command = [*python_command(args.target_dir, args.env_name, args.env_manager), "-u", "-c", smoke_code]
    result = run(command, cwd=args.target_dir, env=env, timeout=args.experiment_timeout_seconds)
    payload: dict[str, Any] = {
        "ok": result.returncode == 0,
        "command": " ".join(command[:4]) + " -c <core-smoke-code>",
        "llm_backend": env["AI4MATH_SMOKE_MODEL"],
        "lightweight_imports": args.lightweight_imports,
        "stdout": result.stdout[-8000:],
        "stderr": result.stderr[-8000:],
    }
    if result.returncode == 0:
        try:
            last_line = [line for line in result.stdout.splitlines() if line.strip()][-1]
            smoke = json.loads(last_line)
            payload["smoke"] = smoke
            payload["ok"] = all((smoke.get("query_model_ok"), smoke.get("agent_ok"), smoke.get("helper_ok")))
            if not payload["ok"]:
                payload["errors"] = ["core smoke response did not contain all expected markers"]
                return 1, payload
        except Exception as exc:
            payload["ok"] = False
            payload["errors"] = [f"failed to parse core smoke JSON: {exc}"]
            return 1, payload
    return result.returncode, payload


def run_wizard(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    try:
        config = collect_wizard_config(args)
    except ValueError as exc:
        return 2, {"ok": False, "errors": [str(exc)]}

    os.environ.update(config["env"])
    args.research_topic = config["research_topic"]
    args.openai_base_url = os.environ.get("OPENAI_BASE_URL")
    args.llm_model_id = config["model"]
    args.llm_backend = config["model"]
    args.lightweight_imports = config["lightweight_imports"]

    payload: dict[str, Any] = {
        "ok": False,
        "mode": config["mode"],
        "research_topic": config["research_topic"],
        "model": config["model"],
        "base_url_set": config["base_url_set"],
        "steps": [],
    }

    if config["mode"] == "codex-native":
        workspace_payload = prepare_codex_workspace(args)
        payload["steps"].append({"step": "codex_workspace", **workspace_payload})
        payload["ok"] = bool(workspace_payload.get("ok"))
        return (0 if payload["ok"] else 1), payload

    if config["deploy"]:
        deploy_payload = deploy(args.target_dir, args.env_name, args.env_manager, args.conda_mirror, args.installer)
        payload["steps"].append({"step": "deploy", **deploy_payload})
        if not deploy_payload.get("ok"):
            return 1, payload
    else:
        payload["steps"].append({"step": "deploy", "ok": True, "skipped": True})

    verify_code, verify_payload = verify(args.target_dir, args.env_name, args.env_manager)
    payload["steps"].append({"step": "verify", **verify_payload})
    if verify_code != 0:
        return verify_code, payload

    if config["core_smoke"]:
        smoke_code, smoke_payload = run_core_smoke(args)
        payload["steps"].append({"step": "core_smoke", **smoke_payload})
        if smoke_code != 0:
            return smoke_code, payload
    else:
        payload["steps"].append({"step": "core_smoke", "ok": True, "skipped": True})

    if config["mode"] == "core":
        payload["ok"] = True
        return 0, payload

    if config["mode"] in {"hybrid", "research"} and args.experiment_yaml == DEFAULT_AGENTLAB_YAML:
        args.experiment_yaml = str(DEFAULT_RESEARCH_YAML)

    experiment_code, experiment_payload = run_experiment(args)
    payload["steps"].append({"step": "run_experiment", **experiment_payload})
    payload["ok"] = experiment_code == 0
    return experiment_code, payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-dir", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--env-name", default=DEFAULT_ENV)
    parser.add_argument("--env-manager", choices=("conda", "uv"), default="conda")
    parser.add_argument("--conda-mirror", choices=tuple(CONDA_MIRRORS), default="default")
    parser.add_argument("--installer", choices=("pip", "uv"), default="pip")
    parser.add_argument("--experiment-yaml", default=DEFAULT_AGENTLAB_YAML)
    parser.add_argument("--research-topic", default=None)
    parser.add_argument("--llm-backend", default=None)
    parser.add_argument("--lit-review-backend", default=None)
    parser.add_argument("--llm-model-id", default=None)
    parser.add_argument("--openai-base-url", default=None)
    parser.add_argument("--compile-latex", default="false")
    parser.add_argument("--lightweight-imports", action="store_true")
    parser.add_argument("--experiment-timeout-seconds", type=int, default=600)
    parser.add_argument("--codex-workspace-dir", type=Path, default=Path("codex_research"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--deploy", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--check-api", action="store_true")
    parser.add_argument("--interactive-api", action="store_true")
    parser.add_argument("--run-experiment", action="store_true")
    parser.add_argument("--core-smoke", action="store_true")
    parser.add_argument("--wizard", action="store_true")
    parser.add_argument("--wizard-mode", metavar="{hybrid,core,research,codex-native,full}", default=None)
    parser.add_argument("--skip-deploy", action="store_true")
    parser.add_argument("--skip-core-smoke", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.check_api:
        return check_api(args.json, args.interactive_api)

    if args.deploy:
        payload = deploy(args.target_dir, args.env_name, args.env_manager, args.conda_mirror, args.installer)
        emit(payload, args.json)
        return 0 if payload.get("ok") else 1

    if args.verify:
        code, payload = verify(args.target_dir, args.env_name, args.env_manager)
        emit(payload, args.json)
        return code

    if args.run_experiment:
        code, payload = run_experiment(args)
        emit(payload, args.json)
        return code

    if args.core_smoke:
        code, payload = run_core_smoke(args)
        emit(payload, args.json)
        return code

    if args.wizard:
        code, payload = run_wizard(args)
        emit(payload, args.json)
        return code

    payload = build_plan(args)
    emit(payload, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
