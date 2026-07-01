---
name: nora-onboard
description: Guide users through full Nora plug-and-play setup — install, Hermes detect, SOUL, channel picker, activate, gateway, doctor. Use when someone is new to Hermes, asks how to install Nora, finish setup, or wire Discord/Telegram/email.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [onboard, install, setup, wizard, doctor, channels, plug-and-play]
    related_skills: [discord-hermes-setup, release-diagnostics, monitoring-briefing]
---

# Nora onboard

## When to use

- "How do I install Nora?"
- "Finish my setup" / "wire Hermes"
- First message after clone — user has files but no Discord reply
- Hermes user adding Nora pack without resetting their LLM

## One command (user machine)

```bash
# macOS / Linux — from ~/.nora or clone root
./scripts/onboard.sh

# Windows
.\scripts\onboard.ps1

# Health check only
./scripts/doctor.sh
./scripts/onboard.sh --verify-only
```

Non-interactive (CI / scripting):

```bash
./scripts/onboard.sh --yes --channel discord --env-file .env
./scripts/onboard.sh --merge-only --yes --env-file .env   # existing Hermes
```

## Wizard phases

1. Prerequisites — git, python3, hermes CLI
2. Hermes detect — `~/.hermes/config.yaml` or link to hermes-agent.com install
3. SOUL edit (optional) — `hermes/SOUL.md` before activate
4. Profile — full activate vs `--merge-only` for existing Hermes
5. LLM key — `POLLINATIONS_API_KEY` (optional if other provider)
6. Channel — Discord recommended; writes `nora/.env`
7. Activate + gateway + doctor verify

## Channel docs

Point users to **`persona/channels.md`** — Hermes canonical link + Nora `env.*.example` per platform.

Discord thread rules: skill **`discord-hermes-setup`**.

## If wizard cannot run

Manual fallback:

```bash
cp env.discord.example .env   # fill in
./scripts/activate.sh
hermes gateway install
./scripts/doctor.sh --channel discord --smoke
```

## Deliverable

1. Confirm Nora root (`~/.nora` or clone path)
2. Run or walk through onboard phases
3. `doctor.sh` green on wiring; channel secrets present
4. User sends **one** test message in **one** place (Discord: inside their thread)
5. Link `persona/channels.md` for second channel