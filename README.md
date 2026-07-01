<p align="center">
  <img src="website/public/hero-bg.jpg" alt="Nora — Hermes Agent Ops Persona" width="100%" />
</p>

# Hermes-Nora

![Repo size](https://img.shields.io/github/repo-size/murderszn/Hermes-Nora)
![Last commit](https://img.shields.io/github/last-commit/murderszn/Hermes-Nora)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-ffcc00)](https://murderszn.github.io/hermes-nora/)

**Nora** is a charming, always-on [Hermes Agent](https://hermes-agent.nousresearch.com/) persona with local machine access, a control dashboard, and ops skills. Talk to her from Discord, Gmail, or your phone — she runs on your computer and does the work.

> Always on, always local. A charming ops assistant with full machine access — ready day or night, whenever you need her.

## Website

The splash page and full documentation deploy automatically from [`website/`](website/) to GitHub Pages:

| | |
|---|---|
| **Home** | [murderszn.github.io/hermes-nora](https://murderszn.github.io/hermes-nora/) — install commands, features, persona overview |
| **Docs** | [murderszn.github.io/hermes-nora/docs.html](https://murderszn.github.io/hermes-nora/docs.html) — prerequisites, install guides, use cases, hardware, best practices |

Edit files in `website/` and push to `main` — the [Pages workflow](.github/workflows/pages.yml) redeploys in about a minute.

## Install

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/murderszn/hermes-nora/main/install.sh | bash
```

**Windows (PowerShell)**

```powershell
irm https://raw.githubusercontent.com/murderszn/hermes-nora/main/install.ps1 | iex
```

**GitHub CLI**

```bash
gh repo clone murderszn/hermes-nora && cd hermes-nora && ./bootstrap.sh
```

You need [Hermes Agent](https://hermes-agent.nousresearch.com/) installed first. See the [docs](https://murderszn.github.io/hermes-nora/docs.html) for Git, Node, Python, and channel setup.

## What is this?

| Piece | What it does |
|-------|----------------|
| **Hermes Agent** | Runtime — memory, skills, scheduling, multi-channel gateway |
| **Nora persona** | Voice, ops defaults, and skills in `skills/` + `hermes/SOUL.md` |
| **Local dashboard** | JARVIS-style control panel at `http://127.0.0.1:7878` |
| **Website** | Public splash + documentation in `website/` |

Nora is not a new model. She is a configured Hermes deployment you can reproduce, extend, and reach from anywhere once Discord or email is connected.

## Repo layout

```text
hermes-nora/
├── website/              # Splash page + docs (GitHub Pages)
│   ├── index.html
│   ├── docs.html
│   ├── styles.css, docs.css, main.js
│   └── public/hero-bg.jpg
├── dashboard/            # Local control dashboard (127.0.0.1:7878)
│   ├── index.html
│   ├── dashboard.py
│   ├── dashboard.js
│   └── assets/
├── hermes/               # Sanitized Hermes config / state snapshots
│   ├── config.yaml
│   ├── SOUL.md
│   └── …                 # tokens masked before commit
├── skills/               # Custom Hermes skills
├── learnings/            # Operator diagnostics and notes
├── scripts/              # Launchers (e.g. Hermes Dashboard.bat)
├── install.sh / install.ps1 / bootstrap.sh
└── .github/workflows/pages.yml
```

> Large runtime data (`state.db`, `bin/`, model caches) are excluded on purpose.

## Dashboard

Local mission control for the agent — status, channels, diagnostics, and live activity.

![Dashboard preview](dashboard/assets/hermes-wallpaper.jfif)

### Run

1. Install Hermes Agent (`hermes setup`).
2. Start the gateway and Discord bridge if not already running.
3. Launch the dashboard:
   - `scripts/Hermes Dashboard.bat` (Windows)
   - or `python dashboard/dashboard.py` → open `http://127.0.0.1:7878`

### Layout (1080p no-scroll)

| Area | Height | Contents |
|------|--------|----------|
| Hero / Banner | 25vh | Agent name, clock, live status, PID, agents |
| R1 | 11.5vh | Watchdog (left) + Discord Uplink (right) |
| R2 | 21vh | Neural Core + Channels (left) / Diagnostics (right) |
| R3 | 42.5vh | Messages (left) + Live Activity Stream (right) |

Panel rows are 50/50 width splits. Inner lists scroll independently.

### Config notes

- Dashboard source of truth: `dashboard/index.html` + `dashboard/dashboard.py`.
- Hermes runtime state lives in your local Hermes data directory.
- The dashboard polls `/api/state` every 5 seconds.
- Secrets in `hermes/.env` and `hermes/auth.json` are redacted before commit.

## Goals

- Keep the agent running and watchable from one local dashboard.
- Channel comms through Discord (and Gmail for async work).
- Capture the exact dashboard, launcher, and Hermes config so it is reproducible.
- Ship a public site so anyone can install Nora and read the docs.

## Learnings

See [`learnings/2026-06-27-diagnostics-and-learnings.md`](learnings/2026-06-27-diagnostics-and-learnings.md) for diagnostics, proposed skills, and correction items.

## License

This project is licensed under the [MIT License](LICENSE).

You are free to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of this software, provided the copyright notice and permission notice are included in all copies or substantial portions. See [LICENSE](LICENSE) for the full text.

Copyright (c) 2026 murderszn

## Links

- [Nora website](https://murderszn.github.io/hermes-nora/)
- [Nora docs](https://murderszn.github.io/hermes-nora/docs.html)
- [Hermes Agent](https://hermes-agent.nousresearch.com/)
- [Nous Research](https://nousresearch.com/)