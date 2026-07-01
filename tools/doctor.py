#!/usr/bin/env python3
"""Nora health check — prerequisites, Hermes wiring, gateway, and channel readiness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nora_common import (
    CHANNELS,
    default_hermes_home,
    default_nora_root,
    find_python,
    gateway_status_text,
    hermes_smoke_test,
    parse_env_file,
    run_cmd,
    soul_has_content,
)


def _status(ok: bool) -> str:
    return "ok" if ok else "fail"


def _warn(ok: bool) -> str:
    return "ok" if ok else "warn"


def check_prereqs() -> list[dict]:
    from nora_common import command_exists

    checks = []
    for name, label in (
        ("git", "Git"),
        ("python3", "Python 3"),
        ("hermes", "Hermes CLI"),
    ):
        ok = command_exists(name) or (name == "python3" and command_exists("python"))
        checks.append({"id": name, "label": label, "status": _status(ok), "detail": ""})
    return checks


def check_nora_files(nora_root: Path) -> list[dict]:
    checks = []
    soul = nora_root / "hermes" / "SOUL.md"
    skills = nora_root / "skills"
    checks.append({
        "id": "soul_src",
        "label": "Nora SOUL source",
        "status": _status(soul_has_content(soul)),
        "detail": str(soul),
    })
    skill_count = len(list(skills.glob("**/SKILL.md"))) if skills.is_dir() else 0
    checks.append({
        "id": "skills",
        "label": "Skills library",
        "status": _status(skill_count > 0),
        "detail": f"{skill_count} skills",
    })
    return checks


def check_hermes_wiring(nora_root: Path, hermes_home: Path) -> list[dict]:
    checks = []
    config_path = hermes_home / "config.yaml"
    soul_live = hermes_home / "SOUL.md"

    checks.append({
        "id": "hermes_config",
        "label": "Hermes config.yaml",
        "status": _status(config_path.is_file()),
        "detail": str(config_path),
    })
    checks.append({
        "id": "soul_live",
        "label": "SOUL.md in Hermes home",
        "status": _status(soul_has_content(soul_live)),
        "detail": str(soul_live),
    })

    skills_linked = False
    discord_ok = False
    pollinations_ok = False
    if config_path.is_file():
        try:
            import yaml  # type: ignore

            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            ext = (cfg.get("skills") or {}).get("external_dirs") or []
            nora_skills = str((nora_root / "skills").resolve())
            skills_linked = any(
                str(Path(d).expanduser().resolve()) == nora_skills for d in ext
            )
            discord = cfg.get("discord") or {}
            discord_ok = discord.get("auto_thread") is False
            model = cfg.get("model") or {}
            providers = cfg.get("custom_providers") or []
            has_poll = any(
                isinstance(p, dict) and p.get("name") == "pollinations" for p in providers
            )
            pollinations_ok = has_poll or "pollinations" in str(model.get("provider", ""))
        except Exception as exc:
            checks.append({
                "id": "config_parse",
                "label": "Parse config.yaml",
                "status": "fail",
                "detail": str(exc),
            })

    checks.append({
        "id": "skills_linked",
        "label": "skills.external_dirs → Nora",
        "status": _status(skills_linked),
        "detail": "",
    })
    checks.append({
        "id": "discord_auto_thread",
        "label": "discord.auto_thread: false",
        "status": _warn(discord_ok),
        "detail": "Nora default — avoids duplicate threads",
    })
    checks.append({
        "id": "pollinations",
        "label": "Pollinations provider wired",
        "status": _warn(pollinations_ok),
        "detail": "Optional if you use another LLM provider",
    })
    return checks


def check_secrets(nora_root: Path, hermes_home: Path, channel: str | None) -> list[dict]:
    checks = []
    for label, path in (("nora/.env", nora_root / ".env"), ("~/.hermes/.env", hermes_home / ".env")):
        vars_ = parse_env_file(path)
        has_pollen = bool(
            vars_.get("POLLINATIONS_API_KEY", "").strip()
            or vars_.get("POLLENATIONS_API_KEY", "").strip()
        )
        checks.append({
            "id": f"pollen_{path.name}",
            "label": f"LLM key in {label}",
            "status": _warn(has_pollen),
            "detail": "POLLINATIONS_API_KEY or other provider in Hermes config",
        })

    if channel and channel in CHANNELS:
        spec = CHANNELS[channel]
        hh_vars = parse_env_file(hermes_home / ".env")
        nr_vars = parse_env_file(nora_root / ".env")
        merged = {**nr_vars, **hh_vars}
        required = [k for k in spec.env_keys if k not in ("DISCORD_HOME_CHANNEL_THREAD_ID",)]
        missing = [k for k in required if not merged.get(k, "").strip()]
        if channel == "whatsapp":
            ok = merged.get("WHATSAPP_ENABLED", "").lower() in {"true", "1", "yes"}
        else:
            ok = not missing
        checks.append({
            "id": f"channel_{channel}",
            "label": f"{spec.name} secrets",
            "status": _status(ok),
            "detail": f"missing: {', '.join(missing)}" if missing else "present",
        })
    return checks


def check_runtime() -> list[dict]:
    checks = []
    running, detail = gateway_status_text()
    checks.append({
        "id": "gateway",
        "label": "Gateway running",
        "status": _status(running),
        "detail": detail.split("\n")[0][:120] if detail else "",
    })
    return checks


def run_doctor(
    *,
    nora_root: Path,
    hermes_home: Path,
    channel: str | None = None,
    smoke: bool = False,
    json_out: bool = False,
) -> int:
    sections = {
        "prereqs": check_prereqs(),
        "nora_files": check_nora_files(nora_root),
        "hermes_wiring": check_hermes_wiring(nora_root, hermes_home),
        "secrets": check_secrets(nora_root, hermes_home, channel),
        "runtime": check_runtime(),
    }

    if smoke:
        ok, text = hermes_smoke_test()
        sections["smoke"] = [{
            "id": "cli_smoke",
            "label": "hermes -z smoke test",
            "status": _status(ok),
            "detail": text[:200] if text else "",
        }]

    all_checks = [c for group in sections.values() for c in group]
    fails = [c for c in all_checks if c["status"] == "fail"]
    warns = [c for c in all_checks if c["status"] == "warn"]

    if json_out:
        print(json.dumps({"sections": sections, "fail": len(fails), "warn": len(warns)}, indent=2))
        return 1 if fails else 0

    print("  ◉  Nora doctor")
    print(f"     Nora root:   {nora_root}")
    print(f"     Hermes home: {hermes_home}")
    print()

    icons = {"ok": "✓", "warn": "○", "fail": "✗"}
    for title, checks in sections.items():
        print(f"  {title.replace('_', ' ').title()}")
        for c in checks:
            icon = icons.get(c["status"], "?")
            detail = f" — {c['detail']}" if c.get("detail") else ""
            print(f"    {icon} {c['label']}{detail}")
        print()

    if fails:
        print(f"  ✗ {len(fails)} issue(s) need attention.")
        print("    Run: ./scripts/onboard.sh   or see skills/ops/discord-hermes-setup/TECH-FAQ.md")
        return 1
    if warns:
        print(f"  ○ {len(warns)} warning(s) — optional fixes above.")
        print("  ✓ Nora core wiring looks good.")
        return 0
    print("  ✓ All checks passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nora-root", type=Path, default=None)
    parser.add_argument("--hermes-home", type=Path, default=None)
    parser.add_argument("--channel", choices=[*CHANNELS.keys(), "none"], default=None)
    parser.add_argument("--smoke", action="store_true", help="Also run hermes -z smoke test")
    parser.add_argument("--json", action="store_true", dest="json_out")
    args = parser.parse_args()

    nora_root = (args.nora_root or default_nora_root()).expanduser().resolve()
    hermes_home = (args.hermes_home or default_hermes_home()).expanduser().resolve()
    channel = None if args.channel in (None, "none") else args.channel

    try:
        find_python(hermes_home)
    except SystemExit:
        pass

    return run_doctor(
        nora_root=nora_root,
        hermes_home=hermes_home,
        channel=channel,
        smoke=args.smoke,
        json_out=args.json_out,
    )


if __name__ == "__main__":
    raise SystemExit(main())