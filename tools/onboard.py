#!/usr/bin/env python3
"""Interactive Nora onboarding — prerequisites, persona, channel, activate, gateway, verify."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nora_common import (
    CHANNELS,
    DISCORD_DEV_PORTAL,
    HERMES_INSTALL_URL,
    POLLINATIONS_URL,
    command_exists,
    default_hermes_home,
    default_nora_root,
    find_python,
    gateway_status_text,
    parse_env_file,
    run_cmd,
    soul_has_content,
    write_env_file,
)


def _prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{text}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(130)
    return value or default


def _confirm(text: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    try:
        ans = input(f"{text} ({hint}): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(130)
    if not ans:
        return default
    return ans in {"y", "yes"}


def _print_header(title: str) -> None:
    print()
    print(f"  ── {title} ──")
    print()


def _open_editor(path: Path) -> None:
    editor = os.environ.get("EDITOR", "")
    if not editor:
        if sys.platform == "darwin":
            editor = "open -t"
        elif os.environ.get("VISUAL"):
            editor = os.environ["VISUAL"]
        else:
            print(f"  Set EDITOR to customize, or edit manually: {path}")
            return
    if editor.startswith("open "):
        subprocess.run(editor.split() + [str(path)], check=False)
    else:
        subprocess.run([editor, str(path)], check=False)


def step_prereqs(*, strict: bool) -> None:
    _print_header("1/7 — Prerequisites")
    missing = []
    for cmd, label, hint in (
        ("git", "Git", "https://git-scm.com/downloads"),
        ("python3", "Python 3", "https://www.python.org/downloads/"),
    ):
        ok = command_exists(cmd) or (cmd == "python3" and command_exists("python"))
        icon = "✓" if ok else "✗"
        print(f"  {icon} {label}")
        if not ok:
            missing.append(f"{label} — {hint}")

    hermes_ok = command_exists("hermes")
    print(f"  {'✓' if hermes_ok else '○'} Hermes CLI")
    if not hermes_ok:
        print(f"     Install Hermes: {HERMES_INSTALL_URL}")
        missing.append("Hermes Agent")

    if missing and strict:
        raise SystemExit("Missing prerequisites. Install the items above and re-run onboard.")
    if missing:
        print()
        print("  ○ Some prerequisites missing — you can continue after installing Hermes.")


def step_hermes_detect(hermes_home: Path) -> bool:
    _print_header("2/7 — Hermes")
    config = hermes_home / "config.yaml"
    if config.is_file():
        print(f"  ✓ Found Hermes home: {hermes_home}")
        return True
    print(f"  ✗ No config at {config}")
    print()
    print("  First-time Hermes setup:")
    print(f"    1. Install from {HERMES_INSTALL_URL}")
    print("    2. Run: hermes setup")
    print("    3. Re-run: ./scripts/onboard.sh")
    if not _confirm("Continue anyway (will fail at activate without Hermes)?", default=False):
        raise SystemExit("Run hermes setup, then re-run onboard.")
    return False


def step_soul_edit(nora_root: Path, *, skip: bool) -> None:
    _print_header("3/7 — Persona (SOUL.md)")
    soul = nora_root / "hermes" / "SOUL.md"
    if soul_has_content(soul):
        print(f"  ✓ Soul document ready: {soul}")
    else:
        print(f"  ○ Customize {soul} before activate")
    print()
    print("  Activate copies SOUL → ~/.hermes/SOUL.md (voice reloads every message).")
    if skip:
        print("  Skipped (--skip-soul-edit).")
        return
    if _confirm("Open SOUL.md in your editor now?", default=False):
        _open_editor(soul)
        input("  Press Enter when done editing...")


def step_profile(*, existing_hermes: bool, merge_only_flag: bool | None, yes: bool) -> bool:
    _print_header("4/7 — Profile")
    if merge_only_flag is not None:
        return merge_only_flag
    if not existing_hermes:
        print("  Fresh Hermes + Nora — full defaults (Pollinations / kimi, Discord auto_thread off).")
        return False
    print("  Existing Hermes detected.")
    print("  • Full activate — Nora LLM defaults (Pollinations / kimi)")
    print("  • Merge-only   — keep your model provider; wire SOUL, skills, Discord defaults")
    if yes:
        return False
    return _confirm("Use merge-only (keep your LLM provider)?", default=True)


def step_llm_key(nora_root: Path, env_values: dict[str, str], *, yes: bool) -> None:
    _print_header("5/7 — LLM key")
    existing = parse_env_file(nora_root / ".env")
    if existing.get("POLLINATIONS_API_KEY", "").strip() or existing.get("POLLENATIONS_API_KEY", "").strip():
        print("  ✓ POLLINATIONS_API_KEY already in nora/.env")
        return
    print(f"  Get a key: {POLLINATIONS_URL} (GitHub sign-in works)")
    print("  Skip if you use another provider already configured in Hermes.")
    if yes:
        return
    key = _prompt("POLLINATIONS_API_KEY (leave empty to skip)", "")
    if key:
        env_values["POLLINATIONS_API_KEY"] = key


def step_channel(
    nora_root: Path,
    env_values: dict[str, str],
    *,
    channel: str | None,
    yes: bool,
) -> str | None:
    _print_header("6/7 — First channel")
    print("  Pick one channel to start. Get it working before adding more.")
    print("  Full matrix: persona/channels.md")
    print()

    if channel == "skip":
        return None
    if channel and channel in CHANNELS:
        chosen = channel
    elif yes:
        chosen = "discord"
    else:
        options = ["discord", "telegram", "email", "slack", "whatsapp", "teams", "skip"]
        for i, cid in enumerate(options, 1):
            spec = CHANNELS.get(cid)
            label = spec.name if spec else "Skip for now"
            tag = f" ({spec.tag})" if spec and spec.tag else ""
            print(f"    {i}. {label}{tag}" if cid != "skip" else f"    {i}. Skip for now")
        pick = _prompt("Choice (1-7)", "1")
        try:
            idx = int(pick) - 1
            chosen = options[idx] if 0 <= idx < len(options) else "discord"
        except ValueError:
            chosen = "discord"

    if chosen == "skip":
        print("  ○ Skipping channel setup — add secrets to nora/.env later.")
        return None

    spec = CHANNELS[chosen]
    print()
    print(f"  {spec.name}")
    print(f"  Hermes guide: {spec.hermes_doc}")
    for note in spec.nora_notes:
        print(f"    • {note}")

    example = nora_root / spec.env_example
    if example.is_file():
        print(f"  Template: {example.name}")

    if chosen == "discord":
        print(f"  Bot token: {DISCORD_DEV_PORTAL}")

    existing = parse_env_file(nora_root / ".env")
    if yes:
        for key in spec.env_keys:
            if existing.get(key, "").strip():
                env_values[key] = existing[key]
        return chosen

    print()
    for key in spec.env_keys:
        current = existing.get(key, "")
        if key.endswith("_THREAD_ID") and not current:
            val = _prompt(f"{key} (optional)", "")
        else:
            val = _prompt(key, current)
        if val:
            env_values[key] = val

    return chosen


def run_activate(
    nora_root: Path,
    hermes_home: Path,
    *,
    merge_only: bool,
) -> None:
    python = find_python(hermes_home)
    activate_py = nora_root / "tools" / "activate_nora.py"
    sync_py = nora_root / "tools" / "sync_env.py"
    args = [python, str(activate_py), "--nora-root", str(nora_root), "--hermes-home", str(hermes_home)]
    if merge_only:
        args.append("--merge-only")
    subprocess.run(args, check=True)
    if (nora_root / ".env").is_file():
        subprocess.run(
            [python, str(sync_py), "--nora-root", str(nora_root), "--hermes-home", str(hermes_home)],
            check=True,
        )


def step_gateway(*, install: bool, yes: bool) -> None:
    _print_header("7/7 — Gateway")
    if not command_exists("hermes"):
        print("  ○ Hermes CLI not available — start gateway manually after install.")
        return
    running, detail = gateway_status_text()
    if running:
        print("  ✓ Gateway already running")
        if _confirm("Restart gateway to pick up config/skills?", default=True if not yes else False):
            run_cmd(["hermes", "gateway", "restart"], timeout=120)
            print("  ✓ Gateway restarted")
        return
    print("  Gateway not running.")
    if install and (yes or _confirm("Install gateway as a background service?", default=True)):
        proc = run_cmd(["hermes", "gateway", "install"], timeout=120)
        print(proc.stdout or proc.stderr or "  ✓ gateway install requested")
    elif yes or _confirm("Start gateway now (hermes gateway run)?", default=False):
        print("  Run in another terminal: hermes gateway run")
        print("  Or: hermes gateway install")


def run_onboard(args: argparse.Namespace) -> int:
    nora_root = args.nora_root.expanduser().resolve()
    hermes_home = args.hermes_home.expanduser().resolve()

    if args.verify_only:
        doctor_py = nora_root / "tools" / "doctor.py"
        python = find_python(hermes_home)
        cmd = [python, str(doctor_py), "--nora-root", str(nora_root), "--hermes-home", str(hermes_home)]
        if args.channel and args.channel != "skip":
            cmd.extend(["--channel", args.channel])
        if args.smoke:
            cmd.append("--smoke")
        return subprocess.call(cmd)

    print("  ◉  Nora onboard")
    print(f"     Nora root:   {nora_root}")
    print(f"     Hermes home: {hermes_home}")

    if not (nora_root / "hermes" / "SOUL.md").is_file():
        raise SystemExit(f"Invalid Nora root (no SOUL.md): {nora_root}")

    step_prereqs(strict=not args.yes)
    has_hermes = step_hermes_detect(hermes_home)
    step_soul_edit(nora_root, skip=args.skip_soul_edit)

    merge_flag: bool | None = True if args.merge_only else (False if args.yes else None)
    merge_only = step_profile(
        existing_hermes=has_hermes,
        merge_only_flag=merge_flag,
        yes=args.yes,
    )

    env_values: dict[str, str] = {}
    if args.env_file:
        env_values.update(parse_env_file(args.env_file.expanduser().resolve()))

    step_llm_key(nora_root, env_values, yes=args.yes)
    channel = step_channel(
        nora_root,
        env_values,
        channel=args.channel,
        yes=args.yes,
    )

    if env_values:
        write_env_file(nora_root / ".env", env_values)
        print()
        print(f"  ✓ Wrote {nora_root / '.env'}")

    if has_hermes:
        _print_header("Activate")
        run_activate(nora_root, hermes_home, merge_only=merge_only)
    else:
        print()
        print("  ○ Skipped activate — run hermes setup first, then:")
        print(f"      {nora_root / 'scripts' / 'activate.sh'}")

    if not args.no_gateway:
        step_gateway(install=not args.no_gateway_install, yes=args.yes)

    _print_header("Verify")
    doctor_py = nora_root / "tools" / "doctor.py"
    python = find_python(hermes_home)
    smoke_flag = ["--smoke"] if args.smoke else []
    ch_flag = ["--channel", channel] if channel else []
    subprocess.run(
        [python, str(doctor_py), "--nora-root", str(nora_root), "--hermes-home", str(hermes_home), *ch_flag, *smoke_flag],
        check=False,
    )

    print()
    print("  Next steps:")
    if channel == "discord":
        print("    1. Create a thread on your message in Discord")
        print("    2. @mention Nora inside the thread (not in #general)")
    elif channel:
        spec = CHANNELS.get(channel)
        if spec:
            print(f"    1. Finish steps in {spec.hermes_doc}")
            print(f"    2. Send a test message on {spec.name}")
    print("    • ./scripts/doctor.sh          — health check anytime")
    print("    • persona/channels.md          — add more channels")
    print("    • skills/ops/discord-hermes-setup/TECH-FAQ.md — troubleshooting")
    print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nora-root", type=Path, default=None)
    parser.add_argument("--hermes-home", type=Path, default=None)
    parser.add_argument(
        "--channel",
        choices=[*CHANNELS.keys(), "skip"],
        default=None,
        help="First channel (default: interactive pick; --yes defaults to discord)",
    )
    parser.add_argument("--merge-only", action="store_true", help="Keep existing Hermes LLM provider")
    parser.add_argument("--yes", "-y", action="store_true", help="Non-interactive; use defaults")
    parser.add_argument("--env-file", type=Path, help="Merge secrets from this .env file")
    parser.add_argument("--skip-soul-edit", action="store_true")
    parser.add_argument("--no-gateway", action="store_true", help="Skip gateway install/start prompts")
    parser.add_argument("--no-gateway-install", action="store_true")
    parser.add_argument("--verify-only", action="store_true", help="Run doctor only")
    parser.add_argument("--smoke", action="store_true", help="Include hermes -z in doctor")
    args = parser.parse_args()

    args.nora_root = args.nora_root or default_nora_root()
    args.hermes_home = args.hermes_home or default_hermes_home()

    return run_onboard(args)


if __name__ == "__main__":
    raise SystemExit(main())