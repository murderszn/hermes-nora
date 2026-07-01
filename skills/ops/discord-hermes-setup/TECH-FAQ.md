# Nora + Hermes + Discord — Tech FAQ

Quick reference for self-hosters cloning Nora or hermes-nora. Nora's agent skill `discord-hermes-setup` points here.

---

## Setup

### What do I run after cloning Nora?

```bash
cd /path/to/nora
cp .env.example .env          # fill secrets locally
./scripts/activate.sh         # SOUL, skills, Discord + Pollinations config
hermes gateway run            # or: hermes gateway install
```

Install path for end users is often `~/.nora` via `install.sh`, then `~/.nora/scripts/activate.sh`.

### Where does Hermes actually read config?

**`HERMES_HOME`** — usually `~/.hermes` on macOS/Linux.

| File | Purpose |
|------|---------|
| `~/.hermes/config.yaml` | Model, skills paths, `discord:` block |
| `~/.hermes/SOUL.md` | Nora persona |
| `~/.hermes/.env` | Bot token, API keys (synced from `nora/.env`) |
| `~/.hermes/logs/gateway.log` | Discord message routing, restarts |

### What goes in `nora/.env`?

```env
DISCORD_BOT_TOKEN=...
DISCORD_ALLOWED_USERS=your_discord_user_id
DISCORD_HOME_CHANNEL=channel_id_for_cron_and_status
POLLINATIONS_API_KEY=sk_...
```

Optional: `DISCORD_HOME_CHANNEL_THREAD_ID` to pin home deliveries to one thread.

Never commit `.env`. Rotate the bot token if it was exposed.

### How do I get Discord IDs?

Developer mode in Discord → right-click channel/user → Copy ID.

Bot token: [Discord Developer Portal](https://discord.com/developers/applications) → your app → Bot → token.

---

## Duplicate threads

### Why do I see two threads and two replies?

Two mechanisms stacked:

1. **Hermes `auto_thread: true` (default)** — @mention in `#general` → bot creates "Thread created by Hermes"
2. **You clicked Create Thread** on the same message → your thread + bot thread

Nora answers each session separately → duplicate "hey" (or similar) in channel + side panel.

### What fix does Nora ship?

`hermes/discord.defaults.yaml`:

```yaml
discord:
  require_mention: true
  auto_thread: false
  thread_require_mention: false
  reactions: true
  history_backfill: true
```

Applied by `tools/activate_nora.py` when you run `./scripts/activate.sh`.

### Workflow B — I create the thread (recommended)

1. Create thread on your message
2. @mention Nora **inside the thread**
3. Do **not** @mention in `#general` for the same conversation
4. Archive old bot-created threads

### Workflow A — Nora creates the thread (Slack-style)

1. Set `auto_thread: true` in `~/.hermes/config.yaml`
2. @mention only in the channel
3. Never create your own thread on that message

### I fixed config but Discord still looks messy

Old threads persist. Archive anything labeled "Thread created by Hermes" or duplicate "hey" threads. Test with a **new** thread after `hermes gateway restart`.

Tracked bot threads live in `~/.hermes/discord_threads.json` — stale IDs can keep the bot responding in archived threads until you stop messaging there.

---

## Gateway

### "Gateway shutting down — your current task will be interrupted"

Expected when:

- `hermes gateway restart` during an active reply
- `activate.sh` pipelines that restart the gateway
- SIGTERM from a manual stop

**Fix:** Don't restart mid-chat. Wait for Nora to finish, then restart once.

### How do I check the gateway?

```bash
hermes gateway status
ps aux | grep 'hermes gateway'
tail -30 ~/.hermes/logs/gateway.log
```

### Gateway not running — bot offline in Discord

```bash
hermes gateway run              # foreground (good for debugging)
hermes gateway install          # launchd/systemd — survives reboot
```

---

## Persona & skills

### Nora sounds like generic Hermes

1. `cat ~/.hermes/SOUL.md` — should be Nora's soul, not empty template
2. Re-run `./scripts/activate.sh` from Nora repo root
3. `hermes config` — personality `none` (SOUL is identity; `/personality pirate` is separate)
4. Avoid `hermes --ignore-rules`

### Skills not showing

```bash
grep external_dirs ~/.hermes/config.yaml
hermes skills list
```

Should include absolute path to `nora/skills`. Restart gateway after path changes.

### CLI smoke test

```bash
hermes -z "Who are you?"
```

Should identify as Nora. (`hermes chat -z` is not the one-shot form.)

---

## LLM (Pollinations)

### Default model

After `activate.sh`:

- Provider: `custom:pollinations`
- Model: `kimi`
- Base URL: `https://gen.pollinations.ai/v1`

Key: [enter.pollinations.ai](https://enter.pollinations.ai)

### Key not working / wrong env name

`sync_env.py` maps `POLLENATIONS_API_KEY` → `POLLINATIONS_API_KEY`. Re-run `activate.sh` after editing `nora/.env`.

### Switch models in chat

```
/model custom:pollinations:deepseek
/model custom:pollinations:claude-fast
```

Fallbacks in config: `deepseek`, `glm`.

---

## Discord behavior reference

| Setting | Default (Hermes) | Nora after activate |
|---------|------------------|---------------------|
| `require_mention` | `true` | `true` |
| `auto_thread` | `true` | **`false`** |
| `thread_require_mention` | `false` | `false` |

**`require_mention`** — in server channels, must @mention the bot (unless channel is in `free_response_channels`).

**`thread_require_mention`** — when `false`, after Nora participates in a thread she keeps replying without @mention in that thread.

**`history_backfill`** — when mention-gated, Nora can pull recent channel context into the session on @mention.

### Per-channel tone (optional)

```yaml
discord:
  channel_prompts:
    "YOUR_CHANNEL_ID": "Keep answers short — user is on mobile."
```

---

## Verification script (copy-paste)

```bash
echo "=== Gateway ==="
hermes gateway status 2>&1

echo "=== Discord config ==="
grep -A6 '^discord:' ~/.hermes/config.yaml

echo "=== SOUL (first line) ==="
head -3 ~/.hermes/SOUL.md

echo "=== Skills path ==="
grep -A2 'external_dirs' ~/.hermes/config.yaml

echo "=== Recent Discord traffic ==="
tail -15 ~/.hermes/logs/gateway.log
```

Healthy Workflow B: `auto_thread: false`, gateway running, one inbound `chat=` ID matching where the user messaged, no new "Thread created by Hermes" after the fix timestamp.

---

## Two-folder workflow (maintainers)

| Folder | Role |
|--------|------|
| Dev workspace (`nora/`) | Edit site, SOUL, skills |
| `hermes-nora/` git repo | GitHub / `install.sh` target |

```bash
./scripts/sync-to-hermes-nora.sh
```

---

## Still stuck?

1. Read `persona/hermes-setup.md` in the Nora repo
2. Ask Nora with skill `discord-hermes-setup` loaded
3. Run `release-diagnostics` skill if errors.log shows repeated failures
4. Open an issue on [hermes-nora](https://github.com/murderszn/hermes-nora) with gateway log excerpt (redact tokens)