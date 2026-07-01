# Make Discord (and every channel) use Nora

Hermes does **not** read persona files from the Nora repo automatically. It reads from **`HERMES_HOME`** — usually `~/.hermes` on your Mac.

## The one command

From the Nora repo root:

```bash
./scripts/onboard.sh
```

The wizard checks prerequisites, optional SOUL edits, your first channel, runs activate, and verifies with doctor.

**Activate only** (Hermes already configured):

```bash
./scripts/activate.sh
./scripts/activate.sh --merge-only   # keep your existing LLM provider
```

Activate:

1. Copies `hermes/SOUL.md` → `~/.hermes/SOUL.md` (backs up the old file)
2. Adds `skills/external_dirs` → this repo's `skills/` folder in `config.yaml`
3. Merges Pollinations + Discord defaults into `config.yaml`

**SOUL.md reloads on every message** — you don't restart for voice tweaks. Restart the gateway after skill path changes if skills don't show up.

## Discord specifically

Discord is just another Hermes channel. The same system prompt (including SOUL.md) is used for CLI, Discord, Gmail, etc.

Checklist:

| Step | Command / action |
|------|------------------|
| Bot token | `nora/.env` (local only) — `activate.sh` syncs into `~/.hermes/.env` |
| Gateway running | `hermes gateway status` → if down: `hermes gateway run` or `hermes gateway install` |
| Persona active | `./scripts/activate.sh` |
| Smoke test | `hermes chat -z "Who are you?"` — should sound like Nora |
| Discord test | DM or @mention the bot in a wired channel |

### If she still sounds like generic Hermes

- Open `~/.hermes/SOUL.md` — if it's still the empty template, re-run `./scripts/activate.sh`
- `hermes config` → **Personality** should be `none` (SOUL.md is the identity; built-in `/personality pirate` overlays are separate)
- Don't run chat with `--ignore-rules` — that skips SOUL.md

### Duplicate threads (you + bot both create one)

Hermes skill + full FAQ: `skills/ops/discord-hermes-setup/` (`SKILL.md` + `TECH-FAQ.md`).

Hermes defaults to **`auto_thread: true`** — every @mention in a **channel** spawns a **bot-owned** thread.

If you also click **Create Thread** on your message, you get **two** threads (yours + Nora's) and she may reply in both.

**Nora ships with `auto_thread: false`** after `activate.sh`. Use this workflow:

1. **You** create the thread on your message
2. **@mention Nora inside that thread** — not in the parent channel
3. She replies only there

**Alternative** (Slack-style): set `discord.auto_thread: true` in `~/.hermes/config.yaml`, then **only** @mention in the channel and **never** create a thread yourself — Nora creates one.

Restart gateway after changing: `hermes gateway restart`

### Optional: per-channel Discord tone

In `~/.hermes/config.yaml`:

```yaml
discord:
  channel_prompts:
    "YOUR_CHANNEL_ID": "Keep answers short — user is on mobile."
```

## LLM — Pollinations.ai

Nora defaults to **Pollinations** (`kimi` model, 256K context, tools + vision). Get your key at [enter.pollinations.ai](https://enter.pollinations.ai) (GitHub: **murderszn**).

Add to `nora/.env`:

```
POLLINATIONS_API_KEY=sk_...
```

Then `./scripts/activate.sh` — syncs the key to `~/.hermes/.env` and sets `custom:pollinations` in config.

Switch models in chat:

```
/model custom:pollinations:deepseek
/model custom:pollinations:claude-fast
```

Free tier includes `kimi`, `glm`, `gemini-search`, `claude-fast`. See [Pollinations API docs](https://gen.pollinations.ai/docs).

## Skills

After activate, Nora skills live at the path added to `skills.external_dirs`. List them:

```bash
hermes skills list
```

Or in chat: ask Nora to run a disk report (triggers `disk-and-repo-report`).

## Two-folder workflow

| Folder | Role |
|--------|------|
| `~/nora` (or this workspace) | Dev — edit site, soul, skills |
| `~/hermes-nora` | Git repo — GitHub / install script target |

Sync dev → git repo:

```bash
./scripts/sync-to-hermes-nora.sh
```

Install target for others clones to `~/.nora` via `install.sh`, then they run `~/.nora/scripts/activate.sh`.