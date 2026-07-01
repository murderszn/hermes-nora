# Hermes Dashboard — Nora Control Interface

Standalone JARVIS-style local dashboard for the Hermes Agent runtime.  
Served at `http://127.0.0.1:7878` by `dashboard.py` (Python stdlib only).

## Launch

- **Launcher:** `Hermes Dashboard.bat` (root of this folder)
- **Server:** `dashboard.py`
- **Port:** 7878
- **Browser:** Chrome or Edge recommended

## Data Sources

Reads directly from the Hermes runtime at `C:/Users/jjohn/AppData/Local/hermes/`:
- `logs/gateway.log` — gateway events
- `logs/agent.log` — agent activity
- `logs/errors.log` — error stream
- `gateway_state.json` — live runtime state
- `channel_directory.json` — channel/thread routing

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
