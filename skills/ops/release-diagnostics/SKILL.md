---
name: release-diagnostics
description: Parse Hermes errors.log and recent gateway failures into actionable lessons. Use after incidents, weekly ops review, or when the dashboard shows repeated errors.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, logs, errors, hermes, learnings]
    related_skills: [disk-and-repo-report, background-safe-edits]
---

# Release diagnostics

## When to use

- Repeated tool failures in a session
- User asks "what's been breaking?"
- After deploying new skills or config

## Run the helper

```bash
python tools/release_diagnostics.py
python tools/release_diagnostics.py --hours 48
python tools/release_diagnostics.py --log /path/to/errors.log
```

Hermes default log locations:

- **macOS:** `~/Library/Application Support/hermes/logs/errors.log` (or `~/.hermes/logs/`)
- **Linux:** `~/.hermes/logs/errors.log`
- **Windows:** `%LOCALAPPDATA%\hermes\logs\errors.log`

Probe with `ls` before assuming path.

## Categories to bucket

| Pattern | Likely fix |
|---------|------------|
| `non-whitelisted tool` | foreground or background-safe-edits |
| `old_string` / patch miss | safe-patch |
| PowerShell/bash mix | shell-cross-platform |
| `timed out without user response` | shorten command, request consent, notify_on_complete |
| `Skill 'X' not found` | skills_list before skill_manage |
| `no such file or directory` | verify path on this machine |

## Deliverable

Produce a short markdown list:

1. Top 3 error themes (with counts if helper provides them)
2. One corrective action each
3. Skill candidates to enable or author if missing

Append durable fixes to memory; append novel patterns to `learnings/` if the user wants repo notes.