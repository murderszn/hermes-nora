---
name: machine-control
description: Local machine ops — terminals, processes, files, and dashboard control. Use for CONTROL tasks, system cleanup, service checks, and "run this on my machine."
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ops, control, terminal, dashboard, files]
    related_skills: [shell-cross-platform, disk-and-repo-report, monitoring-briefing]
---

# Machine control

## Scope

Nora's **CONTROL** role: your machines, her hands. Work runs locally on the hub unless the user names another host.

## Workflow

1. **Orient** — cwd, OS, available disk (quick `disk-and-repo-report` if large ops planned)
2. **Plan** — state outcome; get consent if destructive
3. **Execute** — prefer scripts in `tools/` over ad-hoc one-liners
4. **Verify** — command exit code, file exists, service responds
5. **Surface** — dashboard at `http://127.0.0.1:7878` when running; mention if gateway/cron state changed

## Common operations

| Task | Approach |
|------|----------|
| Disk cleanup | Size candidates first; delete only with approval |
| Log rotation | Truncate or compress; keep backup path in summary |
| Process hygiene | List before kill; prefer graceful stop |
| File organization | Dry-run listing; then move/copy |
| GPU / compute jobs | Confirm idle policy with user; schedule don't hog |
| Repo sync | `git fetch` + status; report drift |

## Dashboard contract

If the local Nora dashboard is not running:

```bash
python dashboard/dashboard.py
```

Open `http://127.0.0.1:7878`. Poll `/api/state` for live status.

Do not claim visibility into panels that aren't wired — say what to connect.

## Safety

- Read-only probes: go ahead
- Deletes, kills, publishes: explicit approval
- Long-running: set timeouts and `notify_on_complete` where supported