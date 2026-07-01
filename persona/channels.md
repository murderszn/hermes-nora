# Channel hub — connect Nora to your comms

Pick **one channel first**. Get a reply end-to-end, then add more.

**Fast path:** `./scripts/onboard.sh` — wizard collects secrets, runs activate, checks gateway.

**Health check anytime:** `./scripts/doctor.sh`

Hermes owns the OAuth/bot/API wiring per platform. Nora adds persona defaults (SOUL, skills, `discord.auto_thread: false`) and `.env` templates in the repo root (`env.*.example`).

---

## Recommended first: Discord

| | |
|---|---|
| **Hermes guide** | [discord.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord) |
| **Nora template** | `env.discord.example` |
| **Developer Portal** | [discord.com/developers/applications](https://discord.com/developers/applications) |

**Nora-specific**

1. Run `./scripts/onboard.sh` or copy `env.discord.example` → `.env`
2. Enable **Message Content Intent** if Hermes requests it
3. Invite bot with `bot` + `applications.commands` scopes
4. **Workflow:** you create the thread → @mention Nora **inside** the thread (not `#general`)
5. Nora sets `auto_thread: false` — avoids duplicate "Thread created by Hermes" threads

Troubleshooting: `skills/ops/discord-hermes-setup/TECH-FAQ.md`

---

## Telegram

| | |
|---|---|
| **Hermes guide** | [telegram.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) |
| **Nora template** | `env.telegram.example` |

Create bot via [@BotFather](https://t.me/BotFather). Put `TELEGRAM_BOT_TOKEN` and your user ID in `TELEGRAM_ALLOWED_USERS`.

---

## Gmail / Email

| | |
|---|---|
| **Hermes guide** | [email.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/email) |
| **Nora template** | `env.email.example` |

Use a **dedicated inbox** for Nora. Gmail: 2FA + [App Password](https://myaccount.google.com/apppasswords).

---

## Slack

| | |
|---|---|
| **Hermes guide** | [slack.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/slack) |
| **Nora template** | `env.slack.example` |

Socket Mode needs **bot token** (`xoxb-`) and **app-level token** (`xapp-`).

---

## WhatsApp

| | |
|---|---|
| **Hermes guide** | [whatsapp.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp) |
| **Nora template** | `env.whatsapp.example` |

Set `WHATSAPP_ENABLED=true`, then run `hermes whatsapp` to pair.

---

## Microsoft Teams

| | |
|---|---|
| **Hermes guide** | [teams.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/teams) |
| **Nora template** | `env.teams.example` |

Azure AD app registration + Bot Framework — follow Hermes doc step by step.

---

## More platforms (Hermes docs)

| Platform | Hermes guide |
|----------|----------------|
| Signal | [signal.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/signal) |
| Matrix | [matrix.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/matrix) |
| Google Chat | [google_chat.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/google_chat) |
| Mattermost | [mattermost.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/mattermost) |
| SMS | [sms.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/sms) |
| Webhooks / API | [webhooks.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/webhooks) |
| Open WebUI | [open-webui.md](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/open-webui) |
| **All platforms** | [Messaging index](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) |

No separate `bot.py` per channel — Hermes gateway adapters handle each platform. Nora's job is persona + defaults; Hermes's job is the connection.

---

## After secrets are in `.env`

```bash
./scripts/activate.sh      # SOUL + skills + config merge + .env sync
hermes gateway install     # or: hermes gateway run
./scripts/doctor.sh --channel discord
```

**Hermes-existing users** (keep your LLM provider):

```bash
./scripts/activate.sh --merge-only
# or: ./scripts/onboard.sh --merge-only
```

---

## Persona before deploy

Edit locally **before** activate (optional):

- `hermes/SOUL.md` — voice and boundaries
- `skills/` — add or customize skills

Activate copies SOUL → `~/.hermes/SOUL.md`. Voice changes apply on the next message; skill path changes need `hermes gateway restart`.