---
name: discord-hermes-setup
description: Fix Nora on Discord — duplicate threads, gateway restarts, persona not loading, Pollinations LLM, and first-time Hermes wiring. Use when users report "Thread created by Hermes", double replies, Gateway shutting down, or generic Hermes voice instead of Nora.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [discord, hermes, setup, troubleshooting, auto_thread, gateway, pollinations, nora]
    related_skills: [release-diagnostics, monitoring-briefing, disk-and-repo-report]
---

# Discord + Hermes setup for Nora

## When to use

- Duplicate Discord threads or Nora replying in two places
- "Thread created by Hermes" on every @mention
- "Gateway shutting down" mid-reply
- Bot sounds like generic Hermes, not Nora
- Fresh install of Nora / hermes-nora — wiring persona, skills, LLM, Discord

Full symptom → fix index: **`TECH-FAQ.md`** in this skill folder.

## Mental model

| What | Where |
|------|--------|
| Persona (voice, boundaries) | `~/.hermes/SOUL.md` — reloads every message |
| Skills | `skills.external_dirs` in `~/.hermes/config.yaml` |
| Secrets (bot token, API keys) | `nora/.env` → synced to `~/.hermes/.env` by `activate.sh` |
| Discord behavior | `discord:` block in `~/.hermes/config.yaml` |
| Live bridge | `hermes gateway run` or `hermes gateway install` |

Hermes does **not** read the Nora git clone automatically. Run **`./scripts/activate.sh`** from the Nora repo root after clone or config edits.

## First-time checklist

```bash
# 1. Hermes installed
hermes setup   # if ~/.hermes/config.yaml missing

# 2. Nora secrets (local only — never commit)
cp .env.example .env
# fill: DISCORD_BOT_TOKEN, DISCORD_ALLOWED_USERS, DISCORD_HOME_CHANNEL, POLLINATIONS_API_KEY

# 3. Wire Nora into Hermes
./scripts/activate.sh

# 4. Start Discord bridge
hermes gateway status
hermes gateway run          # foreground
# or: hermes gateway install   # survives reboot

# 5. Smoke tests
hermes -z "Who are you?"    # should say Nora
# Discord: @mention inside ONE thread (see workflows below)
```

## Duplicate threads — root cause

Hermes defaults to **`discord.auto_thread: true`**: every @mention in a **channel** spawns a **bot-owned** thread ("Thread created by Hermes").

If the user **also** clicks **Create Thread** on their message → **two threads**, Nora may answer **both**.

**Nora ships `auto_thread: false`** via `hermes/discord.defaults.yaml` merged by `activate.sh`.

### Pick ONE workflow

**Workflow B (Nora default — user owns the thread)**

1. User creates a thread on their message
2. @mention Nora **inside that thread only**
3. Never @mention in the parent channel for the same topic
4. Archive old "Thread created by Hermes" threads from before the fix

**Workflow A (Slack-style — bot owns the thread)**

1. Set `discord.auto_thread: true` in `~/.hermes/config.yaml`
2. @mention Nora in the channel only
3. **Never** create a thread manually

After any `discord:` config change:

```bash
hermes gateway restart
```

### Verify fix is live

```bash
hermes gateway status
grep -A6 '^discord:' ~/.hermes/config.yaml
# expect: auto_thread: false  (for Workflow B)
```

Check gateway log — reply should land in the thread or channel you expect, not spawn a new thread:

```bash
tail -20 ~/.hermes/logs/gateway.log
```

## "Gateway shutting down"

Harmless during **planned** restarts (`hermes gateway restart`, `activate.sh` pipelines). Hermes interrupts in-flight tasks and posts a warning to Discord.

**Not a Nora bug.** Avoid restarting mid-conversation. For production: `hermes gateway install`.

## Persona not Nora

| Check | Action |
|-------|--------|
| Empty SOUL | Re-run `./scripts/activate.sh`; confirm `~/.hermes/SOUL.md` has Nora content |
| Built-in personality overlay | `hermes config` → personality should be `none` |
| Skipped rules | Don't use `--ignore-rules` |
| Skills missing | `hermes skills list` — should show `discord-hermes-setup`, ops skills, etc. |

## Pollinations LLM

Nora defaults to `custom:pollinations` / `kimi`. Key in `nora/.env` as `POLLINATIONS_API_KEY` (typo `POLLENATIONS_API_KEY` is mapped by sync). Re-run `activate.sh` after key changes.

## Deliverable when helping a user

1. **Diagnose** — which workflow they want (A or B); are they messaging two places?
2. **Confirm config** — `auto_thread`, gateway PID, SOUL.md present
3. **Fix** — `activate.sh`, archive stale threads, restart gateway once
4. **Verify** — one new message → one reply in one place
5. **Point to** `TECH-FAQ.md` for self-serve

## Pitfalls

- Testing in old Hermes-created threads while also posting in `#general`
- Expecting config changes without gateway restart
- Committing `.env` (tokens exposed)
- Using `hermes chat -z` — prefer `hermes -z "..."` for one-shot CLI test