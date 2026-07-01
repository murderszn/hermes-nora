#!/usr/bin/env python3
"""Disk, git repo, and environment snapshot — stdlib only."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def disk_usage() -> list[dict]:
    rows = []
    if platform.system() == "Windows":
        try:
            ps = (
                "Get-PSDrive -PSProvider FileSystem | "
                "Select-Object Name,Used,Free,@{n='Root';e={$_.Root}} | "
                "ConvertTo-Json -Compress"
            )
            raw = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            data = json.loads(raw)
            if isinstance(data, dict):
                data = [data]
            for d in data:
                used = int(d.get("Used") or 0)
                free = int(d.get("Free") or 0)
                total = used + free or 1
                pct = round(100 * used / total, 1)
                rows.append(
                    {
                        "mount": d.get("Root") or d.get("Name", "?"),
                        "used_pct": pct,
                        "free_gb": round(free / (1024**3), 2),
                    }
                )
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            pass
    else:
        try:
            out = subprocess.check_output(["df", "-h"], text=True)
            for line in out.strip().splitlines()[1:]:
                parts = line.split()
                if len(parts) < 6:
                    continue
                mount = parts[-1]
                pct_s = parts[4].rstrip("%")
                try:
                    pct = float(pct_s)
                except ValueError:
                    continue
                rows.append({"mount": mount, "used_pct": pct, "free_gb": None})
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return sorted(rows, key=lambda r: r["used_pct"], reverse=True)


def git_status(root: Path) -> dict | None:
    git_dir = root / ".git"
    if not git_dir.exists():
        return None
    try:
        branch = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        status = subprocess.check_output(
            ["git", "-C", str(root), "status", "-sb"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = "\n" in status or status.endswith("]") is False
        behind = "[behind" in status
        ahead = "[ahead" in status
        return {
            "path": str(root),
            "branch": branch,
            "dirty": dirty or status.splitlines()[0].count("?") or len(status.splitlines()) > 1,
            "behind": behind,
            "ahead": ahead,
            "summary": status.splitlines()[0] if status else branch,
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"path": str(root), "error": "git failed"}


def find_repos(roots: list[Path], max_depth: int = 4) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()

    def walk(base: Path, depth: int) -> None:
        if depth > max_depth or base in seen:
            return
        seen.add(base)
        if (base / ".git").exists():
            found.append(base)
            return
        try:
            children = sorted(base.iterdir())
        except OSError:
            return
        for child in children:
            if child.name in {".git", "node_modules", ".venv", "venv", "__pycache__"}:
                continue
            if child.is_dir():
                walk(child, depth + 1)

    for root in roots:
        if root.is_dir():
            walk(root.resolve(), 0)
    return found


def hermes_hint() -> str | None:
    home = Path.home()
    candidates = [
        home / ".hermes",
        home / "Library" / "Application Support" / "hermes",
        Path(os.environ.get("LOCALAPPDATA", "")) / "hermes",
    ]
    for p in candidates:
        if p.is_dir():
            return str(p)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--roots",
        nargs="*",
        default=[],
        help="Directories to scan for git repos",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    roots = [Path(r).expanduser() for r in args.roots]
    if not roots:
        cwd = Path.cwd()
        roots = [cwd, Path.home() / "Projects", Path.home() / "code", Path.home() / "dev"]
        roots = [r for r in roots if r.is_dir()]

    report = {
        "platform": platform.system(),
        "hostname": platform.node(),
        "disk": disk_usage(),
        "repos": [git_status(p) for p in find_repos(roots)],
        "hermes_dir": hermes_hint(),
        "python": sys.version.split()[0],
        "git": shutil.which("git"),
        "gh": shutil.which("gh"),
    }
    report["repos"] = [r for r in report["repos"] if r]

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"Platform: {report['platform']} ({report['hostname']})")
    if report["hermes_dir"]:
        print(f"Hermes:   {report['hermes_dir']}")
    print("\nDisk:")
    for d in report["disk"]:
        flag = " !" if d["used_pct"] >= 90 else (" *" if d["used_pct"] >= 85 else "")
        free = f", {d['free_gb']} GB free" if d.get("free_gb") is not None else ""
        print(f"  {d['mount']}: {d['used_pct']}%{free}{flag}")
    print("\nRepos:")
    if not report["repos"]:
        print("  (none found under scan roots)")
    for r in report["repos"]:
        if "error" in r:
            print(f"  {r['path']}: {r['error']}")
        else:
            marks = []
            if r.get("dirty"):
                marks.append("dirty")
            if r.get("behind"):
                marks.append("behind")
            if r.get("ahead"):
                marks.append("ahead")
            suffix = f" [{', '.join(marks)}]" if marks else ""
            print(f"  {r['path']}: {r['summary']}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())