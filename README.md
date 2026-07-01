# hermes-nora

Hermes agent persona and ops tools addon — MIT licensed.

Nora is a drop-in persona for [Hermes Agent](https://hermes-agent.nousresearch.com) built on [Nous](https://nousresearch.com) models. She ships with a soul document, a skills library for every connector role, ops tools, and a distinct voice for running your machines.

## What's in the box

| Path | Purpose |
|------|---------|
| `hermes/SOUL.md` | Nora's personality, voice, and boundaries |
| `skills/` | Ops foundation + 8 connector packs (17 skills) |
| `tools/` | Python helpers for disk/repo and diagnostics |
| `persona/roles.md` | Role → skill mapping |
| `index.html`, `docs.html` | Public splash + documentation |

## Install

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/murderszn/hermes-nora/main/install.sh | bash
~/.nora/scripts/onboard.sh
```

**Windows (PowerShell)**

```powershell
irm https://raw.githubusercontent.com/murderszn/hermes-nora/main/install.ps1 | iex
~\.nora\scripts\onboard.ps1
```

**GitHub CLI**

```bash
gh repo clone murderszn/hermes-nora && cd hermes-nora && ./scripts/onboard.sh
```

The onboard wizard checks prerequisites, optional SOUL edits, your first channel (Discord recommended), runs `activate.sh`, and verifies with `doctor.sh`.

**Hermes already installed?** Use merge-only to keep your LLM provider:

```bash
./scripts/onboard.sh --merge-only
# or: ./scripts/activate.sh --merge-only
```

**Health check:** `./scripts/doctor.sh`

Channel matrix and Hermes doc links: [persona/channels.md](persona/channels.md)

## Site

- [index.html](index.html) — splash page
- [docs.html](docs.html) — technology overview, use cases, and best practices

Deploy to GitHub Pages from the repo root.

## License

MIT — see [LICENSE](LICENSE).