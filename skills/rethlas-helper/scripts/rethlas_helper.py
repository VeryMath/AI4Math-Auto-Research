#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


SKILL_ROOT = Path(__file__).resolve().parents[1]
PATCH_PATH = SKILL_ROOT / "assets" / "rethlas-opencode-compat.patch"
CONFIG_HOME = Path(
    os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
).expanduser()
INSTALLATION_CONFIG_PATH = CONFIG_HOME / "opencode" / "rethlas-helper.toml"

REQUIRED_UPSTREAM_PATHS = (
    "README.md",
    "agents/generation/AGENTS.md",
    "agents/generation/.codex/config.toml",
    "agents/verification/AGENTS.md",
    "agents/verification/.codex/config.toml",
)


class HelperError(RuntimeError):
    pass


def run(
    command: Sequence[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def patch_path() -> Path:
    if not PATCH_PATH.is_file():
        raise HelperError(f"patch asset is missing: {PATCH_PATH}")
    return PATCH_PATH


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
    missing = [path for path in REQUIRED_UPSTREAM_PATHS if not (root / path).is_file()]
    if missing:
        raise HelperError(
            "target is not a recognized Rethlas root; missing: "
            + ", ".join(missing)
        )
    return root


def installation_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "config_file": str(INSTALLATION_CONFIG_PATH),
        "configured": False,
        "valid": False,
        "rethlas_home": None,
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
        if separator and key.strip() == "rethlas_home":
            try:
                raw_home = json.loads(encoded_value.strip())
            except json.JSONDecodeError as exc:
                payload["error"] = (
                    f"cannot parse rethlas_home in installation config: {exc}"
                )
                return payload
            break

    if not isinstance(raw_home, str) or not raw_home.strip():
        payload["error"] = "installation config has no valid rethlas_home"
        return payload

    payload["configured"] = True
    payload["rethlas_home"] = str(Path(raw_home).expanduser().resolve())
    try:
        root = resolve_repo(raw_home)
    except HelperError as exc:
        payload["error"] = str(exc)
        return payload

    payload["valid"] = True
    payload["rethlas_home"] = str(root)
    return payload


def configured_repo() -> Path:
    payload = installation_payload()
    if payload.get("error"):
        raise HelperError(f"installation configuration error: {payload['error']}")
    if not payload["configured"]:
        raise HelperError(
            "Rethlas installation is not configured; run installation-set TARGET"
        )
    if not payload["valid"]:
        detail = payload.get("error") or "configured path is unavailable"
        raise HelperError(f"configured Rethlas installation is invalid: {detail}")
    return Path(str(payload["rethlas_home"]))


def resolve_target(target: str | None) -> Path:
    if target:
        return resolve_repo(target)
    return configured_repo()


def save_installation(root: Path) -> dict[str, Any]:
    INSTALLATION_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = f"rethlas_home = {json.dumps(str(root), ensure_ascii=False)}\n"
    try:
        INSTALLATION_CONFIG_PATH.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise HelperError(f"cannot write installation config: {exc}") from exc
    return installation_payload()


def git_output(root: Path, *arguments: str) -> str:
    return run(["git", "-C", str(root), *arguments]).stdout.strip()


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


def command_info(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return {"available": path is not None, "path": path}


def doctor_payload(root: Path, patch: Path) -> dict[str, Any]:
    status_lines = git_output(root, "status", "--short").splitlines()
    head = git_output(root, "rev-parse", "HEAD")
    branch = git_output(root, "branch", "--show-current")
    remote_result = run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        check=False,
    )
    origin = remote_result.stdout.strip() if remote_result.returncode == 0 else ""

    payload = {
        "repository": str(root),
        "origin": origin,
        "branch": branch,
        "head": head,
        "working_tree_entries": len(status_lines),
        "working_tree_status": status_lines,
        "patch_state": patch_state(root, patch),
        "generation_venv": (root / "agents/generation/.venv/bin/python").is_file(),
        "verification_venv": (
            root / "agents/verification/.venv/bin/python"
        ).is_file(),
        "commands": {
            name: command_info(name)
            for name in ("git", "python3", "uv", "opencode")
        },
    }
    payload.update(
        {
            f"installation_{key}": value
            for key, value in installation_payload().items()
        }
    )
    return payload


def print_payload(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    for key in (
        "config_file",
        "configured",
        "valid",
        "rethlas_home",
        "error",
        "installation_config_file",
        "installation_configured",
        "installation_valid",
        "installation_rethlas_home",
        "installation_error",
        "repository",
        "origin",
        "branch",
        "head",
        "working_tree_entries",
        "patch_state",
        "generation_venv",
        "verification_venv",
    ):
        if key in payload:
            print(f"{key}: {payload[key]}")

    commands = payload.get("commands")
    if isinstance(commands, dict):
        print("commands:")
        for name, info in commands.items():
            if isinstance(info, dict):
                print(f"  {name}: {info.get('path') or 'not found'}")

    status = payload.get("working_tree_status")
    if isinstance(status, list) and status:
        print("working_tree_status:")
        for line in status:
            print(f"  {line}")


def apply_patch(root: Path, patch: Path) -> None:
    state = patch_state(root, patch)
    if state == "installed":
        print("OpenCode patch is already installed.")
        return
    if state != "not-installed":
        raise HelperError(
            f"cannot apply patch while state is '{state}'; "
            "inspect conflicting or partially installed files"
        )

    run(["git", "-C", str(root), "apply", "--check", str(patch)])
    run(["git", "-C", str(root), "apply", str(patch)])
    if patch_state(root, patch) != "installed":
        raise HelperError("patch command completed but installed state was not detected")
    print("OpenCode patch installed successfully.")


def remove_patch(root: Path, patch: Path) -> None:
    state = patch_state(root, patch)
    if state == "not-installed":
        print("OpenCode patch is not installed.")
        return
    if state != "installed":
        raise HelperError(
            f"cannot remove patch while state is '{state}'; "
            "patched files may have local modifications"
        )

    run(
        [
            "git",
            "-C",
            str(root),
            "apply",
            "--reverse",
            "--check",
            str(patch),
        ]
    )
    run(["git", "-C", str(root), "apply", "--reverse", str(patch)])
    if patch_state(root, patch) != "not-installed":
        raise HelperError("reverse patch completed but clean state was not detected")
    print("OpenCode patch removed successfully.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Remember a Rethlas installation, diagnose it, and manage the "
            "bundled OpenCode patch."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("installation-show")
    show_parser.add_argument("--json", action="store_true")

    set_parser = subparsers.add_parser("installation-set")
    set_parser.add_argument("target")
    set_parser.add_argument("--json", action="store_true")

    for command in ("doctor", "patch-status"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("target", nargs="?", default=None)
        subparser.add_argument("--json", action="store_true")

    for command in ("patch-apply", "patch-remove"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("target", nargs="?", default=None)

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

        patch = patch_path()
        root = resolve_target(args.target)

        if args.command == "doctor":
            print_payload(
                doctor_payload(root, patch),
                as_json=args.json,
            )
        elif args.command == "patch-status":
            print_payload(
                {
                    "repository": str(root),
                    "patch_state": patch_state(root, patch),
                    "head": git_output(root, "rev-parse", "HEAD"),
                },
                as_json=args.json,
            )
        elif args.command == "patch-apply":
            apply_patch(root, patch)
        elif args.command == "patch-remove":
            remove_patch(root, patch)
        else:  # pragma: no cover
            raise HelperError(f"unsupported command: {args.command}")
    except (HelperError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
