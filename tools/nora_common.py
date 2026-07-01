"""Shared helpers for Nora onboard, doctor, and activate tooling."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


HERMES_DOCS_BASE = "https://hermes-agent.nousresearch.com/docs/user-guide/messaging"
HERMES_INSTALL_URL = "https://hermes-agent.nousresearch.com"
POLLINATIONS_URL = "https://enter.pollinations.ai"
DISCORD_DEV_PORTAL = "https://discord.com/developers/applications"


@dataclass
class ChannelSpec:
    id: str
    name: str
    tag: str
    hermes_doc: str
    env_example: str
    env_keys: list[str]
    nora_notes: list[str] = field(default_factory=list)


CHANNELS: dict[str, ChannelSpec] = {
    "discord": ChannelSpec(
        id="discord",
        name="Discord",
        tag="recommended",
        hermes_doc=f"{HERMES_DOCS_BASE}/discord",
        env_example="env.discord.example",
        env_keys=[
            "DISCORD_BOT_TOKEN",
            "DISCORD_ALLOWED_USERS",
            "DISCORD_HOME_CHANNEL",
            "DISCORD_HOME_CHANNEL_THREAD_ID",
        ],
        nora_notes=[
            "Nora sets discord.auto_thread: false — you create the thread, @mention Nora inside it.",
            "Enable Message Content Intent in the Discord Developer Portal if Hermes asks.",
            "Invite URL needs bot scope + applications.commands.",
        ],
    ),
    "telegram": ChannelSpec(
        id="telegram",
        name="Telegram",
        tag="chat",
        hermes_doc=f"{HERMES_DOCS_BASE}/telegram",
        env_example="env.telegram.example",
        env_keys=[
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_ALLOWED_USERS",
            "TELEGRAM_HOME_CHANNEL",
        ],
        nora_notes=[
            "Create the bot via @BotFather on Telegram.",
            "TELEGRAM_HOME_CHANNEL is the chat ID for cron/status delivery.",
        ],
    ),
    "email": ChannelSpec(
        id="email",
        name="Gmail / Email",
        tag="async",
        hermes_doc=f"{HERMES_DOCS_BASE}/email",
        env_example="env.email.example",
        env_keys=[
            "EMAIL_ADDRESS",
            "EMAIL_PASSWORD",
            "EMAIL_IMAP_HOST",
            "EMAIL_SMTP_HOST",
            "EMAIL_ALLOWED_USERS",
            "EMAIL_HOME_ADDRESS",
        ],
        nora_notes=[
            "Use a dedicated inbox for Nora (e.g. nora.yourname@gmail.com).",
            "Gmail: enable 2FA and create an App Password.",
        ],
    ),
    "slack": ChannelSpec(
        id="slack",
        name="Slack",
        tag="chat",
        hermes_doc=f"{HERMES_DOCS_BASE}/slack",
        env_example="env.slack.example",
        env_keys=[
            "SLACK_BOT_TOKEN",
            "SLACK_APP_TOKEN",
            "SLACK_ALLOWED_USERS",
        ],
        nora_notes=[
            "Socket Mode requires both bot token (xoxb-) and app-level token (xapp-).",
        ],
    ),
    "whatsapp": ChannelSpec(
        id="whatsapp",
        name="WhatsApp",
        tag="chat",
        hermes_doc=f"{HERMES_DOCS_BASE}/whatsapp",
        env_example="env.whatsapp.example",
        env_keys=[
            "WHATSAPP_ENABLED",
            "WHATSAPP_ALLOWED_USERS",
        ],
        nora_notes=[
            "Run `hermes whatsapp` to pair after WHATSAPP_ENABLED=true.",
        ],
    ),
    "teams": ChannelSpec(
        id="teams",
        name="Microsoft Teams",
        tag="work",
        hermes_doc=f"{HERMES_DOCS_BASE}/teams",
        env_example="env.teams.example",
        env_keys=[
            "TEAMS_CLIENT_ID",
            "TEAMS_CLIENT_SECRET",
            "TEAMS_TENANT_ID",
            "TEAMS_ALLOWED_USERS",
        ],
        nora_notes=[
            "Register an Azure AD app — see Hermes Teams doc for Bot Framework steps.",
        ],
    ),
    "signal": ChannelSpec(
        id="signal",
        name="Signal",
        tag="privacy",
        hermes_doc=f"{HERMES_DOCS_BASE}/signal",
        env_example="env.signal.example",
        env_keys=[],
        nora_notes=["Follow Hermes Signal guide — linking uses signal-cli."],
    ),
    "matrix": ChannelSpec(
        id="matrix",
        name="Matrix",
        tag="chat",
        hermes_doc=f"{HERMES_DOCS_BASE}/matrix",
        env_example="env.matrix.example",
        env_keys=[],
        nora_notes=["Homeserver + access token per Hermes Matrix doc."],
    ),
}


def default_nora_root() -> Path:
    env = os.environ.get("NORA_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    candidate = Path.home() / ".nora"
    if candidate.is_dir():
        return candidate.resolve()
    # Dev: repo root when tools/ is under nora
    here = Path(__file__).resolve().parent.parent
    if (here / "hermes" / "SOUL.md").is_file():
        return here
    return candidate


def default_hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser().resolve()


def find_python(hermes_home: Path | None = None) -> str:
    override = os.environ.get("HERMES_PYTHON", "").strip()
    if override:
        return override
    hh = hermes_home or default_hermes_home()
    for rel in (
        "hermes-agent/venv/bin/python",
        "hermes-agent/venv/Scripts/python.exe",
    ):
        candidate = hh / rel
        if candidate.is_file():
            return str(candidate)
    py = shutil.which("python3") or shutil.which("python")
    if py:
        return py
    raise SystemExit("Python not found. Install Python 3 or Hermes Agent first.")


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_cmd(
    args: list[str],
    *,
    timeout: int = 60,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=check,
    )


def parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)", s)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def write_env_file(path: Path, values: dict[str, str], *, header: str | None = None) -> None:
    existing = parse_env_file(path) if path.is_file() else {}
    for key, val in values.items():
        if val.strip():
            existing[key] = val.strip()

    preamble: list[str] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("#") or not s:
                preamble.append(line)
            else:
                break
    if not preamble:
        preamble = [
            "# Nora local secrets — never commit this file",
            "# Generated by nora onboard",
            "",
        ]
    if header and header not in "\n".join(preamble):
        preamble.extend(["", f"# {header.lstrip('# ')}"])

    lines = preamble[:]
    for key in sorted(existing.keys()):
        lines.append(f"{key}={existing[key]}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def soul_has_content(path: Path, min_lines: int = 5) -> bool:
    if not path.is_file():
        return False
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("<!--") or s.startswith("*"):
            continue
        count += 1
        if count >= min_lines:
            return True
    return False


def gateway_status_text() -> tuple[bool, str]:
    if not command_exists("hermes"):
        return False, "hermes CLI not in PATH"
    proc = run_cmd(["hermes", "gateway", "status"], timeout=30)
    out = (proc.stdout or "") + (proc.stderr or "")
    running = "running" in out.lower() and "not running" not in out.lower()
    return running, out.strip() or f"exit {proc.returncode}"


def hermes_smoke_test() -> tuple[bool, str]:
    if not command_exists("hermes"):
        return False, "hermes CLI not in PATH"
    proc = run_cmd(["hermes", "-z", "Who are you?"], timeout=120)
    text = (proc.stdout or "") + (proc.stderr or "")
    ok = proc.returncode == 0 and len(text.strip()) > 0
    return ok, text.strip()[:500]