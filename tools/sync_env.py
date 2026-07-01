#!/usr/bin/env python3
"""Merge Nora repo .env into ~/.hermes/.env (Discord and other Hermes keys)."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

# Keys Nora keeps in-repo .env that Hermes gateway reads from HERMES_HOME/.env
NORA_TO_HERMES_KEYS = {
    "DISCORD_BOT_TOKEN",
    "DISCORD_ALLOWED_USERS",
    "DISCORD_ALLOWED_ROLES",
    "DISCORD_HOME_CHANNEL",
    "DISCORD_HOME_CHANNEL_THREAD_ID",
    "DISCORD_HOME_CHANNEL_NAME",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_ALLOWED_USERS",
    "TELEGRAM_HOME_CHANNEL",
    "TELEGRAM_HOME_CHANNEL_NAME",
    "TELEGRAM_HOME_CHANNEL_THREAD_ID",
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN",
    "SLACK_ALLOWED_USERS",
    "EMAIL_ADDRESS",
    "EMAIL_PASSWORD",
    "EMAIL_IMAP_HOST",
    "EMAIL_IMAP_PORT",
    "EMAIL_SMTP_HOST",
    "EMAIL_SMTP_PORT",
    "EMAIL_ALLOWED_USERS",
    "EMAIL_HOME_ADDRESS",
    "WHATSAPP_ENABLED",
    "WHATSAPP_ALLOWED_USERS",
    "TEAMS_CLIENT_ID",
    "TEAMS_CLIENT_SECRET",
    "TEAMS_TENANT_ID",
    "TEAMS_ALLOWED_USERS",
    "TEAMS_HOME_CHANNEL",
    "POLLINATIONS_API_KEY",
    "POLLINATIONS_KEY",
    "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY",
}


def parse_env(path: Path) -> dict[str, str]:
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


def merge_env_file(dest: Path, updates: dict[str, str]) -> list[str]:
    """Upsert keys in dest .env; return list of keys written."""
    lines: list[str] = []
    if dest.is_file():
        lines = dest.read_text(encoding="utf-8").splitlines()

    index: dict[str, int] = {}
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)=", s)
        if m:
            index[m.group(1)] = i

    written: list[str] = []
    block_header = "# Nora addon (synced from nora/.env)"
    if block_header not in lines and updates:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(block_header)

    for key, value in sorted(updates.items()):
        entry = f"{key}={value}"
        if key in index:
            if lines[index[key]].strip() != entry:
                lines[index[key]] = entry
                written.append(key)
        else:
            lines.append(entry)
            written.append(key)

    if written:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if dest.is_file():
            backup = dest.with_name(f".env.bak.{stamp}")
            backup.write_text(dest.read_text(encoding="utf-8"), encoding="utf-8")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nora-root", type=Path, required=True)
    parser.add_argument("--hermes-home", type=Path, default=Path.home() / ".hermes")
    args = parser.parse_args()

    src = args.nora_root.expanduser().resolve() / ".env"
    dest = args.hermes_home.expanduser().resolve() / ".env"

    if not src.is_file():
        print(f"No {src} — skip env sync")
        return 0

    src_vars = parse_env(src)
    # Common typo: POLLENATIONS → Pollinations
    if src_vars.get("POLLENATIONS_API_KEY", "").strip() and not src_vars.get(
        "POLLINATIONS_API_KEY", ""
    ).strip():
        src_vars["POLLINATIONS_API_KEY"] = src_vars["POLLENATIONS_API_KEY"].strip()

    updates = {k: v for k, v in src_vars.items() if k in NORA_TO_HERMES_KEYS and v.strip()}
    if not updates:
        print("No Hermes-relevant keys in nora/.env")
        return 0

    written = merge_env_file(dest, updates)
    if written:
        print(f"  ✓ Synced to {dest}: {', '.join(written)}")
    else:
        print(f"  ✓ {dest} already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())