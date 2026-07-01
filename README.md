# Hermes-Nora

![Repo size](https://img.shields.io/github/repo-size/murderszn/Hermes-Nora)
![Last commit](https://img.shields.io/github/last-commit/murderszn/Hermes-Nora)
![License: Unlicense](https://img.shields.io/badge/License-Unlicense-blue.svg)

Local setup of [Hermes Agent](https://hermes-agent.nousresearch.com/) named **Nora**, bound to Discord, with a custom JARVIS-style control dashboard.

## Website

The Nora splash page and documentation live in [`website/`](website/) and deploy automatically to GitHub Pages:

**https://murderszn.github.io/hermes-nora/**

- Home: install commands, feature overview
- Docs: prerequisites, install guides, use cases, hardware recommendations

## Dashboard preview

![Hermes dashboard wallpaper](dashboard/assets/hermes-wallpaper.jfif)

## Goals

- Keep the agent running and watchable from one local dashboard.
- Channel all comms through Discord.
- Capture the exact dashboard + launcher + Hermes config used here so it’s reproducible.

> Large runtime data (`state.db`, `bin/`, model caches) are excluded on purpose.

## Layout (1080p no-scroll)

| Area | Height | Contents |
|------|--------|----------|
| Hero / Banner | 25vh | Agent name, clock, live status, PID, agents |
| R1 | 11.5vh | Watchdog (left) + Discord Uplink (right) |
| R2 | 21vh | Neural Core + Channels (left) / Diagnostics (right) |
| R3 | 42.5vh | Messages (left) + Live Activity Stream (right) |

Panel rows are 50/50 width splits. Inner lists scroll independently.

## Customization

See the `hermes-dashboard` skill for:
- UI/UX rules and CSS class conventions
- Panel row structure
- Channel sidebar behavior
- Slack-like thread rendering

## Notes

- No voice UI button in the hero (removed by request).
- Fullscreen toggle via `F` or `Esc`; button hides itself automatically.
- Auto-opens the latest channel thread on load.
