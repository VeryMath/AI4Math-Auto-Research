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
PATCH_PATH = SKILL_ROOT / "assets" / "patches" / "archon-v0.3.3-opencode.patch"
SUPPORTED_VERSION = "0.3.3"
CONFIG_HOME = Path(
    os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
).expanduser()
INSTALLATION_CONFIG_PATH = CONFIG_HOME / "opencode" / "archon-helper.toml"


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


def archon_version(root: Path) -> str:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        raise HelperError(f"Archon pyproject.toml is missing: {pyproject}")
    text = pyproject.read_text(encoding="utf-8")
    if not re.search(r'(?m)^name\s*=\s*"archon"\s*$', text):
        raise HelperError(f"pyproject.toml does not define the Archon package: {root}")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    if not match:
        raise HelperError(f"Archon version is missing from {pyproject}")
    return match.group(1)


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
    archon_version(root)
    return root


def installation_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "config_file": str(INSTALLATION_CONFIG_PATH),
        "configured": False,
        "valid": False,
        "archon_home": None,
        "archon_bin": None,
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
        if separator and key.strip() == "archon_home":
            try:
                raw_home = json.loads(encoded_value.strip())
            except json.JSONDecodeError as exc:
                payload["error"] = (
                    f"cannot parse archon_home in installation config: {exc}"
                )
                return payload
            break

    if not isinstance(raw_home, str) or not raw_home.strip():
        payload["error"] = "installation config has no valid archon_home"
        return payload

    payload["configured"] = True
    payload["archon_home"] = str(Path(raw_home).expanduser().resolve())
    try:
        root = resolve_repo(raw_home)
    except HelperError as exc:
        payload["error"] = str(exc)
        return payload

    version = archon_version(root)
    archon_bin = root / ".venv" / "bin" / "archon"
    payload.update(
        {
            "valid": True,
            "archon_home": str(root),
            "archon_bin": str(archon_bin),
            "archon_bin_ready": archon_bin.is_file(),
            "version": version,
            "supported_version": version == SUPPORTED_VERSION,
        }
    )
    return payload


def configured_repo() -> Path:
    payload = installation_payload()
    if payload.get("error"):
        raise HelperError(f"installation configuration error: {payload['error']}")
    if not payload["configured"]:
        raise HelperError(
            "Archon installation is not configured; run installation-set TARGET"
        )
    if not payload["valid"]:
        raise HelperError("configured Archon installation is unavailable")
    return Path(str(payload["archon_home"]))


def save_installation(root: Path) -> dict[str, Any]:
    INSTALLATION_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = f"archon_home = {json.dumps(str(root), ensure_ascii=False)}\n"
    try:
        INSTALLATION_CONFIG_PATH.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise HelperError(f"cannot write installation config: {exc}") from exc
    return installation_payload()


def can_apply(root: Path, patch: Path, *, reverse: bool = False) -> bool:
    command = ["git", "-C", str(root), "apply"]
    if reverse:
        command.append("--reverse")
    command.extend(["--check", str(patch)])
    return run(command, check=False).returncode == 0


def patch_state(root: Path, patch: Path) -> str:
    forward = can_apply(root, patch)
    reverse = can_apply(root, patch, reverse=True)
    if forward and not reverse:
        return "not-installed"
    if reverse and not forward:
        return "installed"
    if forward and reverse:
        return "ambiguous"
    return "conflict-or-partial"


def project_payload(project: str) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    config_path = root / ".archon" / "config.json"
    payload: dict[str, Any] = {
        "project": str(root),
        "project_exists": root.is_dir(),
        "project_initialized": config_path.is_file(),
        "project_config": str(config_path),
        "project_harness": None,
        "project_multilane_enabled": None,
        "project_opencode_skill": (
            root / ".opencode" / "skills" / "lean4" / "SKILL.md"
        ).is_file(),
        "project_opencode_subagent": (
            root / ".opencode" / "tools" / "archon-subagent.py"
        ).is_file(),
    }
    if not config_path.is_file():
        return payload
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        payload["project_config_error"] = str(exc)
        return payload
    if not isinstance(config, dict):
        payload["project_config_error"] = "project config is not a JSON object"
        return payload
    loop = config.get("loop")
    if isinstance(loop, dict):
        payload["project_harness"] = loop.get("harness")
    multilane = config.get("multilane")
    if isinstance(multilane, dict):
        payload["project_multilane_enabled"] = multilane.get("enabled")
    return payload


def doctor_payload(root: Path, project: str) -> dict[str, Any]:
    patch = patch_path()
    status = run(["git", "-C", str(root), "status", "--short"]).stdout.splitlines()
    branch = run(["git", "-C", str(root), "branch", "--show-current"]).stdout.strip()
    head = run(["git", "-C", str(root), "rev-parse", "HEAD"]).stdout.strip()
    payload = installation_payload()
    payload.update(
        {
            "repository": str(root),
            "branch": branch,
            "head": head,
            "working_tree_entries": len(status),
            "working_tree_status": status,
            "patch_state": patch_state(root, patch),
            "opencode": shutil.which("opencode"),
        }
    )
    payload.update(project_payload(project))
    return payload


def apply_patch(root: Path) -> None:
    version = archon_version(root)
    if version != SUPPORTED_VERSION:
        raise HelperError(
            f"patch supports Archon {SUPPORTED_VERSION}; configured version is {version}"
        )
    patch = patch_path()
    state = patch_state(root, patch)
    if state == "installed":
        print("OpenCode patch is already installed.")
        return
    if state != "not-installed":
        raise HelperError(
            f"cannot apply patch while state is '{state}'; inspect the worktree"
        )
    status = run(["git", "-C", str(root), "status", "--porcelain"]).stdout.strip()
    if status:
        raise HelperError("Archon worktree contains changes; inspect them before patching")

    run(["git", "-C", str(root), "apply", "--check", str(patch)])
    run(["git", "-C", str(root), "apply", str(patch)])

    python = root / ".venv" / "bin" / "python"
    executable = str(python) if python.is_file() else sys.executable
    compiled = run(
        [executable, "-m", "compileall", "-q", "src/archon"],
        cwd=root,
        check=False,
    )
    if compiled.returncode != 0:
        detail = compiled.stderr.strip() or "Python compilation failed"
        raise HelperError(detail)
    if patch_state(root, patch) != "installed":
        raise HelperError("patch command completed without a complete installed state")
    print("Archon OpenCode patch installed successfully.")


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
            "Remember an Archon installation, inspect an Archon project, and "
            "manage the OpenCode patch."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("installation-show")
    show_parser.add_argument("--json", action="store_true")

    set_parser = subparsers.add_parser("installation-set")
    set_parser.add_argument("target")
    set_parser.add_argument("--json", action="store_true")

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("project", nargs="?", default=".")
    doctor_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("patch-status")
    status_parser.add_argument("--json", action="store_true")

    subparsers.add_parser("patch-apply")
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
            print_payload(doctor_payload(root, args.project), as_json=args.json)
        elif args.command == "patch-status":
            patch = patch_path()
            print_payload(
                {
                    "repository": str(root),
                    "version": archon_version(root),
                    "patch_state": patch_state(root, patch),
                },
                as_json=args.json,
            )
        elif args.command == "patch-apply":
            apply_patch(root)
        else:
            raise HelperError(f"unsupported command: {args.command}")
    except (HelperError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
