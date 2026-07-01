---
name: disk-and-repo-report
description: Safe disk, git repo, and Hermes process snapshot across platforms. Use for morning briefings, cleanup planning, or before large file ops.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [disk, git, diagnostics, reporting, python]
    related_skills: [shell-cross-platform, monitoring-briefing]
---

# Disk and repo report

## When to use

- "How's my disk?" / "What repos need attention?"
- Pre-cleanup or backup planning
- Dashboard diagnostics panel data

## Preferred implementation

Run the bundled helper (stdlib only):

```bash
python tools/disk_and_repo_report.py
```

Optional flags:

```bash
python tools/disk_and_repo_report.py --roots ~/Projects ~/code
python tools/disk_and_repo_report.py --json
```

## Manual fallback

If the script is unavailable:

1. Disk: `df -h` (Unix) or PowerShell `Get-PSDrive -PSProvider FileSystem`
2. Git: walk known project roots — `git -C <path> status -sb` only where `.git` exists
3. Hermes: read `gateway_state.json` / process list from local Hermes data dir if present

## Output shape

Summarize for the user:

- Volumes over **85%** full (flag **90%+** as urgent)
- Repos with uncommitted changes or behind remote
- Stale clone paths that failed `git` (skip gracefully)

## Pitfalls

- Inline `find | while` across shells on Windows — use the Python helper
- Scanning entire home directory without exclusion — respect `node_modules`, `.git`, caches