#!/usr/bin/env python3
"""检查并应用随附的 Archon v0.3.3 零 Claude OpenCode 补丁。"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
PATCH = SKILL_DIR / "assets" / "patches" / "archon-v0.3.3-opencode.patch"
SUPPORTED_VERSION = "0.3.3"


def run(
    argv: list[str], *, cwd: Path, capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        capture_output=capture,
        check=False,
    )


def fail(message: str) -> None:
    print(f"错误：{message}", file=sys.stderr)
    raise SystemExit(1)


def archon_version(repo: Path) -> str:
    pyproject = repo / "pyproject.toml"
    if not pyproject.is_file():
        fail(f"{repo} 不是 Archon 检出：缺少 pyproject.toml")
    text = pyproject.read_text(encoding="utf-8")
    if not re.search(r'(?m)^name\s*=\s*"archon"\s*$', text):
        fail(f"{repo}/pyproject.toml 不是 Archon 包")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    if not match:
        fail("无法确定 Archon 版本")
    return match.group(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="检查或应用 Archon v0.3.3 的 OpenCode 补丁。",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Archon Git 检出路径（默认：当前目录）",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="仅检查补丁能否干净应用，不修改文件",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="允许在已有改动的检出上应用补丁（不推荐）",
    )
    args = parser.parse_args()

    repo = args.repo.expanduser().resolve()
    if not (repo / ".git").exists():
        fail(f"{repo} 不是 Git 检出")
    version = archon_version(repo)
    if version != SUPPORTED_VERSION:
        fail(
            f"补丁目标版本为 Archon {SUPPORTED_VERSION}，当前检出版本为 {version}"
        )
    if not PATCH.is_file():
        fail(f"缺少随附补丁：{PATCH}")

    already = repo / "src" / "archon" / "agents" / "opencode.py"
    if already.is_file():
        print("OpenCode harness 已存在，未重复应用补丁。")
        return

    status = run(["git", "status", "--porcelain"], cwd=repo, capture=True)
    if status.returncode != 0:
        fail(status.stderr.strip() or "git status 执行失败")
    if status.stdout.strip() and not args.allow_dirty:
        fail("检出中存在改动；请先提交或以其他方式保存这些改动")

    check = run(
        ["git", "apply", "--check", str(PATCH)], cwd=repo, capture=True,
    )
    if check.returncode != 0:
        fail(check.stderr.strip() or "补丁无法干净应用")
    print(f"补丁可干净应用到 Archon {version}。")
    if args.check_only:
        return

    applied = run(["git", "apply", str(PATCH)], cwd=repo, capture=True)
    if applied.returncode != 0:
        fail(applied.stderr.strip() or "git apply 执行失败")

    python = repo / ".venv" / "bin" / "python"
    executable = str(python) if python.is_file() else sys.executable
    compiled = run(
        [
            executable,
            "-m",
            "compileall",
            "-q",
            "src/archon",
        ],
        cwd=repo,
        capture=True,
    )
    if compiled.returncode != 0:
        fail(compiled.stderr.strip() or "Python 编译检查失败")

    opencode = shutil.which("opencode")
    if opencode:
        version_check = run([opencode, "--version"], cwd=repo, capture=True)
        detail = (version_check.stdout or version_check.stderr).strip()
        print(f"检测到 OpenCode：{detail or opencode}")
    else:
        print("警告：补丁已应用，但 PATH 中找不到 opencode")
    print(
        "Archon OpenCode 补丁已应用并通过编译检查"
        "（覆盖 init/loop/resume/subagent；OpenCode 模式不依赖 Claude 运行时）。"
    )


if __name__ == "__main__":
    main()
