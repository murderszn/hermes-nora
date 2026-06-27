# Hermes-Nora

![Repo size](https://img.shields.io/github/repo-size/murderszn/Hermes-Nora)
![Last commit](https://img.shields.io/github/last-commit/murderszn/Hermes-Nora)
![License: Unlicense](https://img.shields.io/badge/License-Unlicense-blue.svg)

Local setup of [Hermes Agent](https://hermes-agent.nousresearch.com/) named **Nora**, bound to Discord, with a custom JARVIS-style control dashboard.

## Dashboard preview

![Hermes dashboard wallpaper](dashboard/assets/hermes-wallpaper.jfif)

## Layout

```text
hermes-nora/
├── dashboard/        # HTML + Python dashboard served on 127.0.0.1:7878
│   ├── index.html
│   ├── dashboard.py
│   ├── hermes.ico
│   └── assets/
│       └── hermes-wallpaper.jfif
├── hermes/           # Sanitized local Hermes config / state snapshots
│   ├── config.yaml
│   ├── channel_directory.json
│   ├── gateway_state.json
│   ├── processes.json
│   ├── discord_threads.json
│   ├── auth.json           # tokens are masked (***)
│   ├── .env                # secrets are masked (***)
│   └── SOUL.md
├── skills/           # Custom Hermes skills derived from operator learnings
├── learnings/        # Daily diagnostics and improvement notes
│   └── 2026-06-27-diagnostics-and-learnings.md
└── README.md
```

> Large runtime data (`state.db`, `bin/`, model caches) are excluded on purpose.

## Run

1. Install Hermes Agent (`hermes setup`).
2. Start the gateway and Discord bridge if not already running.
3. Launch the dashboard:
   - `scripts/Hermes Dashboard.bat`
   - Opens `http://127.0.0.1:7878`

## Config notes

- Dashboard source of truth: `dashboard/index.html` + `dashboard/dashboard.py`.
- Hermes runtime state: `C:\Users\jjohn\AppData\Local\hermes\`.
- The dashboard polls `/api/state` every 5 seconds.
- Secrets in `hermes/.env` and `hermes/auth.json` are redacted before commit.

## Learnings

See [`learnings/2026-06-27-diagnostics-and-learnings.md`](learnings/2026-06-27-diagnostics-and-learnings.md) for a categorical diagnosis of today’s warnings/errors, proposed skills, and correction items.
