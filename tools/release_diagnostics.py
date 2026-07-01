#!/usr/bin/env python3
"""Summarize Hermes errors.log into actionable categories."""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path


CATEGORIES: list[tuple[str, re.Pattern[str]]] = [
    ("whitelist_blocked", re.compile(r"non-whitelisted tool", re.I)),
    ("patch_miss", re.compile(r"old_string|Could not find a match|identical", re.I)),
    ("shell_mismatch", re.compile(r"powershell|Where-Object|Refresh :|unary operator", re.I)),
    ("timeout_consent", re.compile(r"timed out without user response|NOT consented", re.I)),
    ("missing_path", re.compile(r"No such file|cannot access|not found in active profile", re.I)),
    ("missing_cli", re.compile(r"command not found|gh:", re.I)),
    ("memory_pressure", re.compile(r"exceed the limit|Consolidate", re.I)),
    ("git_submodule", re.compile(r"submodule mapping", re.I)),
]

TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})")


def default_log_path() -> Path | None:
    home = Path.home()
    candidates = [
        home / ".hermes" / "logs" / "errors.log",
        home / "Library" / "Application Support" / "hermes" / "logs" / "errors.log",
        Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "logs" / "errors.log",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def parse_since(lines: list[str], hours: int) -> list[str]:
    if hours <= 0:
        return lines
    cutoff = datetime.now() - timedelta(hours=hours)
    kept: list[str] = []
    for line in lines:
        m = TS_RE.match(line)
        if not m:
            kept.append(line)
            continue
        try:
            ts = datetime.fromisoformat(m.group(1).replace(" ", "T"))
        except ValueError:
            kept.append(line)
            continue
        if ts >= cutoff:
            kept.append(line)
    return kept


def categorize(lines: list[str]) -> tuple[Counter[str], list[str]]:
    counts: Counter[str] = Counter()
    samples: dict[str, str] = {}
    for line in lines:
        matched = False
        for name, pat in CATEGORIES:
            if pat.search(line):
                counts[name] += 1
                samples.setdefault(name, line.strip()[:200])
                matched = True
                break
        if not matched and "error" in line.lower():
            counts["other"] += 1
            samples.setdefault("other", line.strip()[:200])
    return counts, [samples[k] for k in sorted(counts, key=counts.get, reverse=True)]


FIXES = {
    "whitelist_blocked": "Enable foreground run or use background-safe-edits skill.",
    "patch_miss": "Apply safe-patch: re-read file before edit.",
    "shell_mismatch": "Use shell-cross-platform; prefer Python helpers.",
    "timeout_consent": "Shorter commands; explicit user consent for long ops.",
    "missing_path": "Verify paths on this machine; use skills_list().",
    "missing_cli": "Install missing CLI or document in README prerequisites.",
    "memory_pressure": "Consolidate memory; move procedures to skills.",
    "git_submodule": "Verify .gitmodules before submodule commands.",
    "other": "Inspect sample line; add learning entry if novel.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, help="Path to errors.log")
    parser.add_argument("--hours", type=int, default=24, help="Only lines within N hours")
    args = parser.parse_args()

    log_path = args.log or default_log_path()
    if not log_path or not log_path.is_file():
        print("No errors.log found. Pass --log explicitly.")
        return 1

    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    lines = parse_since(lines, args.hours)
    counts, _ = categorize(lines)

    print(f"Source: {log_path}")
    print(f"Window: last {args.hours}h · {len(lines)} lines scanned\n")

    if not counts:
        print("No categorized errors in window.")
        return 0

    for name, n in counts.most_common():
        print(f"{name}: {n}")
        print(f"  → {FIXES.get(name, FIXES['other'])}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())