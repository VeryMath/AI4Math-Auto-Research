#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_ROOT / "assets" / "rethlas-opencode-compat.json"

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


def load_manifest() -> dict[str, Any]:
    try:
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HelperError(f"cannot read patch manifest: {exc}") from exc
    if not isinstance(payload, dict):
        raise HelperError("patch manifest must be a JSON object")
    return payload


def patch_path(manifest: dict[str, Any]) -> Path:
    filename = manifest.get("patch_file")
    if not isinstance(filename, str) or not filename:
        raise HelperError("patch manifest has no valid patch_file")
    path = MANIFEST_PATH.parent / filename
    if not path.is_file():
        raise HelperError(f"patch asset is missing: {path}")
    return path


def verify_patch_asset(manifest: dict[str, Any]) -> Path:
    path = patch_path(manifest)
    expected = manifest.get("patch_sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise HelperError("patch manifest has no valid patch_sha256")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise HelperError(
            f"patch checksum mismatch: expected {expected}, got {actual}"
        )
    return path


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


def doctor_payload(root: Path, manifest: dict[str, Any], patch: Path) -> dict[str, Any]:
    status_lines = git_output(root, "status", "--short").splitlines()
    head = git_output(root, "rev-parse", "HEAD")
    branch = git_output(root, "branch", "--show-current")
    remote_result = run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        check=False,
    )
    origin = remote_result.stdout.strip() if remote_result.returncode == 0 else ""

    files = manifest.get("files")
    if not isinstance(files, list):
        files = []

    return {
        "repository": str(root),
        "origin": origin,
        "branch": branch,
        "head": head,
        "baseline_commit": manifest.get("baseline_commit"),
        "at_baseline": head == manifest.get("baseline_commit"),
        "working_tree_entries": len(status_lines),
        "working_tree_status": status_lines,
        "patch_state": patch_state(root, patch),
        "patched_files_present": {
            str(path): (root / str(path)).exists() for path in files
        },
        "generation_venv": (root / "agents/generation/.venv/bin/python").is_file(),
        "verification_venv": (
            root / "agents/verification/.venv/bin/python"
        ).is_file(),
        "commands": {
            name: command_info(name)
            for name in ("git", "python3", "uv", "codex", "opencode")
        },
    }


def print_payload(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    for key in (
        "repository",
        "origin",
        "branch",
        "head",
        "baseline_commit",
        "at_baseline",
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
        description="Diagnose Rethlas and manage the bundled OpenCode patch."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("doctor", "patch-status"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("target", nargs="?", default=".")
        subparser.add_argument("--json", action="store_true")

    for command in ("patch-apply", "patch-remove"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("target", nargs="?", default=".")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = load_manifest()
        patch = verify_patch_asset(manifest)
        root = resolve_repo(args.target)

        if args.command == "doctor":
            print_payload(
                doctor_payload(root, manifest, patch),
                as_json=args.json,
            )
        elif args.command == "patch-status":
            print_payload(
                {
                    "repository": str(root),
                    "patch_state": patch_state(root, patch),
                    "baseline_commit": manifest.get("baseline_commit"),
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
