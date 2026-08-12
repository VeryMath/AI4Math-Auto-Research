#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


SKILL_ROOT = Path(__file__).resolve().parents[1]
PATCH_PATH = SKILL_ROOT / "assets" / "danus-v0.1.0-codex-opencode.patch"
UPSTREAM_URL = "https://github.com/frenzymath/Danus.git"
SUPPORTED_TAG = "v0.1.0-codex"
SUPPORTED_COMMIT = "7a51336e53cd1d558d0e766a61eb0fed46ebb05b"
CONFIG_HOME = Path(
    os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
).expanduser()
INSTALLATION_CONFIG_PATH = CONFIG_HOME / "opencode" / "danus-helper.toml"


class HelperError(RuntimeError):
    pass


def run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def patch_path() -> Path:
    if not PATCH_PATH.is_file():
        raise HelperError(f"patch asset is missing: {PATCH_PATH}")
    return PATCH_PATH


def verify_danus_root(root: Path) -> None:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        raise HelperError(f"Danus pyproject.toml is missing: {pyproject}")
    text = pyproject.read_text(encoding="utf-8")
    if not re.search(r'(?m)^name\s*=\s*"danus"\s*$', text):
        raise HelperError(f"pyproject.toml does not define the Danus package: {root}")
    if not (root / "danus").is_dir() or not (root / "scripts" / "bootstrap.sh").is_file():
        raise HelperError(f"required Danus source files are missing: {root}")


def resolve_repo(target: str) -> Path:
    candidate = Path(target).expanduser().resolve()
    if not candidate.is_dir():
        raise HelperError(f"target directory does not exist: {candidate}")
    result = run(
        ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "not a Git repository"
        raise HelperError(f"{candidate}: {detail}")
    root = Path(result.stdout.strip()).resolve()
    verify_danus_root(root)
    return root


def head_commit(root: Path) -> str:
    return run(["git", "-C", str(root), "rev-parse", "HEAD"]).stdout.strip()


def installation_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "config_file": str(INSTALLATION_CONFIG_PATH),
        "configured": False,
        "valid": False,
        "danus_home": None,
        "supported_tag": SUPPORTED_TAG,
        "supported_commit": SUPPORTED_COMMIT,
        "upstream_url": UPSTREAM_URL,
    }
    if not INSTALLATION_CONFIG_PATH.is_file():
        return payload

    try:
        config_text = INSTALLATION_CONFIG_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        payload["error"] = f"cannot read installation config: {exc}"
        return payload

    raw_home: Any = None
    for line in config_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, encoded_value = stripped.partition("=")
        if separator and key.strip() == "danus_home":
            try:
                raw_home = json.loads(encoded_value.strip())
            except json.JSONDecodeError as exc:
                payload["error"] = f"cannot parse danus_home: {exc}"
                return payload
            break

    if not isinstance(raw_home, str) or not raw_home.strip():
        payload["error"] = "installation config has no valid danus_home"
        return payload

    payload["configured"] = True
    payload["danus_home"] = str(Path(raw_home).expanduser().resolve())
    try:
        root = resolve_repo(raw_home)
    except HelperError as exc:
        payload["error"] = str(exc)
        return payload

    payload.update(
        {
            "valid": True,
            "danus_home": str(root),
            "head": head_commit(root),
            "danus_bin": str(root / "bin" / "danus"),
            "runtime_python": str(root / "runtime" / "venv" / "bin" / "python"),
        }
    )
    return payload


def save_installation(root: Path) -> dict[str, Any]:
    INSTALLATION_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = f"danus_home = {json.dumps(str(root), ensure_ascii=False)}\n"
    try:
        INSTALLATION_CONFIG_PATH.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise HelperError(f"cannot write installation config: {exc}") from exc
    return installation_payload()


def configured_repo() -> Path:
    payload = installation_payload()
    if payload.get("error"):
        raise HelperError(f"installation configuration error: {payload['error']}")
    if not payload["configured"]:
        raise HelperError(
            "Danus installation is not configured; run installation-set TARGET"
        )
    if not payload["valid"]:
        raise HelperError("configured Danus installation is unavailable")
    return Path(str(payload["danus_home"]))


def can_apply(root: Path, patch: Path, *, reverse: bool = False) -> bool:
    command = ["git", "-C", str(root), "apply"]
    if reverse:
        command.append("--reverse")
    command.extend(["--check", str(patch)])
    return run(command, check=False).returncode == 0


def has_opencode_adaptation(root: Path) -> bool:
    required = (
        root / "opencode.json",
        root / "danus" / "opencode.py",
        root / "bin" / "opencode",
        root / "scripts" / "check-opencode.sh",
        root / ".opencode" / "plugins" / "danus-loop.ts",
        root / ".opencode" / "commands" / "loop.md",
    )
    removed = (
        root / "danus" / "codex.py",
        root / "bin" / "codex",
        root / "scripts" / "setup-codex.sh",
    )
    return all(path.is_file() for path in required) and all(
        not path.exists() for path in removed
    )


def patch_state(root: Path, patch: Path) -> str:
    forward = can_apply(root, patch)
    reverse = can_apply(root, patch, reverse=True)
    if forward and not reverse:
        return "not-installed"
    if reverse and not forward:
        return "installed"
    if forward and reverse:
        return "ambiguous"
    if has_opencode_adaptation(root):
        return "installed-modified"
    return "conflict-or-partial"


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def live_danus_processes(root: Path) -> list[dict[str, Any]]:
    runtime = root / "runtime"
    candidates = list((runtime / "run").glob("*.pid"))
    candidates.extend((runtime / "projects").glob("*/workers/*/.pid"))
    live: list[dict[str, Any]] = []
    for pid_file in candidates:
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            continue
        if process_alive(pid):
            live.append({"pid": pid, "pid_file": str(pid_file)})
    return live


def doctor_payload(root: Path) -> dict[str, Any]:
    patch = patch_path()
    status = run(["git", "-C", str(root), "status", "--short"]).stdout.splitlines()
    branch = run(["git", "-C", str(root), "branch", "--show-current"]).stdout.strip()
    head = head_commit(root)
    state = patch_state(root, patch)
    opencode = shutil.which("opencode")
    home_opencode = Path.home() / ".opencode" / "bin" / "opencode"
    if opencode is None and home_opencode.is_file() and os.access(home_opencode, os.X_OK):
        opencode = str(home_opencode)
    opencode_version: str | None = None
    if opencode:
        version_result = run([opencode, "--version"], check=False)
        if version_result.returncode == 0:
            opencode_version = version_result.stdout.strip() or version_result.stderr.strip()
    project_config_ready = (root / "opencode.json").is_file()
    agent_rules_ready = (root / "AGENTS.md").is_file()
    runtime_python = root / "runtime" / "venv" / "bin" / "python"
    runtime_ready = False
    if runtime_python.is_file():
        runtime_check = run(
            [
                str(runtime_python),
                "-c",
                "from danus._mcp import FastMCP; import fastapi,uvicorn,pydantic",
            ],
            cwd=root,
            check=False,
        )
        runtime_ready = runtime_check.returncode == 0
    danus_bin_ready = (root / "bin" / "danus").is_file()
    service_manager_ready = (root / "scripts" / "services.sh").is_file()
    recovery_ready = (root / "scripts" / "recover.sh").is_file()
    write_paper_skill_ready = (
        root / ".claude" / "skills" / "write-paper" / "SKILL.md"
    ).is_file()
    human_summary_skill_ready = (
        root / ".claude" / "skills" / "human-summary" / "SKILL.md"
    ).is_file()
    deployment_ready = all(
        (
            state in {"installed", "installed-modified"},
            bool(opencode),
            project_config_ready,
            agent_rules_ready,
            runtime_ready,
            danus_bin_ready,
            service_manager_ready,
            recovery_ready,
            write_paper_skill_ready,
            human_summary_skill_ready,
        )
    )
    if deployment_ready:
        deployment_state = "ready"
    elif state == "not-installed":
        deployment_state = "awaiting-patch"
    elif state in {"installed", "installed-modified"}:
        deployment_state = "provision-required"
    else:
        deployment_state = "needs-inspection"
    payload = installation_payload()
    payload.update(
        {
            "repository": str(root),
            "branch": branch,
            "head": head,
            "head_matches_supported_commit": head == SUPPORTED_COMMIT,
            "working_tree_entries": len(status),
            "working_tree_status": status,
            "patch_state": state,
            "deployment_state": deployment_state,
            "opencode": opencode,
            "opencode_version": opencode_version,
            "opencode_project_config": project_config_ready,
            "opencode_agent_rules": agent_rules_ready,
            "runtime_ready": runtime_ready,
            "danus_bin_ready": danus_bin_ready,
            "service_manager_ready": service_manager_ready,
            "recovery_ready": recovery_ready,
            "write_paper_skill_ready": write_paper_skill_ready,
            "human_summary_skill_ready": human_summary_skill_ready,
            "live_processes": live_danus_processes(root),
        }
    )
    return payload


def apply_opencode_patch(root: Path) -> dict[str, Any]:
    patch = patch_path()
    state = patch_state(root, patch)
    if state == "installed":
        return {
            "repository": str(root),
            "changed": False,
            "patch_state": "installed",
            "message": "Danus OpenCode patch is already installed.",
        }
    if head_commit(root) != SUPPORTED_COMMIT:
        raise HelperError(
            "patch requires Danus commit "
            f"{SUPPORTED_COMMIT}; configured HEAD is {head_commit(root)}"
        )
    if state != "not-installed":
        raise HelperError(
            f"cannot apply patch while state is '{state}'; inspect the worktree"
        )
    status = run(["git", "-C", str(root), "status", "--porcelain"]).stdout.strip()
    if status:
        raise HelperError("Danus worktree contains changes; inspect them before patching")

    run(["git", "-C", str(root), "apply", "--check", str(patch)])
    run(["git", "-C", str(root), "apply", str(patch)])

    compiled = run(
        [sys.executable, "-m", "compileall", "-q", "danus"],
        cwd=root,
        check=False,
    )
    if compiled.returncode != 0:
        run(["git", "-C", str(root), "apply", "--reverse", str(patch)], check=False)
        detail = compiled.stderr.strip() or "Python compilation failed"
        raise HelperError(detail)
    whitespace = run(["git", "-C", str(root), "diff", "--check"], check=False)
    if whitespace.returncode != 0:
        run(["git", "-C", str(root), "apply", "--reverse", str(patch)], check=False)
        detail = whitespace.stdout.strip() or whitespace.stderr.strip()
        raise HelperError(detail or "git diff --check failed")
    if patch_state(root, patch) != "installed":
        run(["git", "-C", str(root), "apply", "--reverse", str(patch)], check=False)
        raise HelperError("patch command completed without a complete installed state")
    return {
        "repository": str(root),
        "changed": True,
        "patch_state": "installed",
        "message": "Danus OpenCode patch installed successfully.",
    }


def remove_opencode_patch(root: Path) -> dict[str, Any]:
    patch = patch_path()
    state = patch_state(root, patch)
    if state == "not-installed":
        return {
            "repository": str(root),
            "changed": False,
            "patch_state": "not-installed",
            "message": "Danus OpenCode patch is not installed.",
        }
    if head_commit(root) != SUPPORTED_COMMIT:
        raise HelperError(
            "patch removal requires Danus commit "
            f"{SUPPORTED_COMMIT}; configured HEAD is {head_commit(root)}"
        )
    if state != "installed":
        raise HelperError(
            f"cannot remove patch while state is '{state}'; inspect the worktree"
        )
    live = live_danus_processes(root)
    if live:
        details = ", ".join(str(item["pid"]) for item in live)
        raise HelperError(
            "Danus services or workers are active; stop them before patch removal "
            f"(pids: {details})"
        )
    if not can_apply(root, patch, reverse=True):
        raise HelperError("the installed patch cannot be reversed cleanly")

    run(["git", "-C", str(root), "apply", "--reverse", str(patch)])
    if patch_state(root, patch) != "not-installed":
        raise HelperError("patch removal completed without a clean baseline state")
    return {
        "repository": str(root),
        "changed": True,
        "patch_state": "not-installed",
        "message": "Danus OpenCode patch removed successfully.",
    }


def print_payload(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            continue
        print(f"{key}: {value}")
    status = payload.get("working_tree_status")
    if isinstance(status, list) and status:
        print("working_tree_status:")
        for line in status:
            print(f"  {line}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Remember a Danus installation and manage its supported OpenCode patch."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("installation-show")
    show_parser.add_argument("--json", action="store_true")

    set_parser = subparsers.add_parser("installation-set")
    set_parser.add_argument("target")
    set_parser.add_argument("--json", action="store_true")

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("patch-status")
    status_parser.add_argument("--json", action="store_true")

    apply_parser = subparsers.add_parser("patch-apply")
    apply_parser.add_argument("--json", action="store_true")

    remove_parser = subparsers.add_parser("patch-remove")
    remove_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "installation-show":
            print_payload(installation_payload(), as_json=args.json)
            return 0
        if args.command == "installation-set":
            root = resolve_repo(args.target)
            print_payload(save_installation(root), as_json=args.json)
            return 0

        root = configured_repo()
        if args.command == "doctor":
            print_payload(doctor_payload(root), as_json=args.json)
        elif args.command == "patch-status":
            print_payload(
                {
                    "repository": str(root),
                    "supported_tag": SUPPORTED_TAG,
                    "supported_commit": SUPPORTED_COMMIT,
                    "head": head_commit(root),
                    "patch_state": patch_state(root, patch_path()),
                },
                as_json=args.json,
            )
        elif args.command == "patch-apply":
            result = apply_opencode_patch(root)
            print_payload(result, as_json=args.json)
        elif args.command == "patch-remove":
            result = remove_opencode_patch(root)
            print_payload(result, as_json=args.json)
        else:
            raise HelperError(f"unsupported command: {args.command}")
    except (HelperError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
