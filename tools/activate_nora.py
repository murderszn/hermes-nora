#!/usr/bin/env python3
"""Wire Nora persona + skills into a live Hermes install (~/.hermes)."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


def _import_yaml():
    try:
        import yaml  # type: ignore
        return yaml
    except ImportError:
        pass
    venv_py = Path.home() / ".hermes" / "hermes-agent" / "venv" / "bin" / "python"
    if venv_py.is_file():
        raise SystemExit(
            "PyYAML not on default python. Re-run with Hermes venv:\n"
            f"  {venv_py} {Path(__file__).resolve()} --nora-root ... --hermes-home ..."
        )
    raise SystemExit(
        "PyYAML required. Install Hermes Agent or: pip3 install pyyaml\n"
        "Or add skills.external_dirs to ~/.hermes/config.yaml manually."
    )


def load_yaml(path: Path) -> dict:
    yaml = _import_yaml()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid config at {path}")
    return data


def dump_yaml(path: Path, data: dict) -> None:
    yaml = _import_yaml()
    path.write_text(yaml.safe_dump(data, sort_keys=False, default_flow_style=False), encoding="utf-8")


def _provider_names(custom_providers: list) -> set[str]:
    names: set[str] = set()
    for entry in custom_providers:
        if isinstance(entry, dict) and entry.get("name"):
            names.add(str(entry["name"]))
    return names


def ensure_discord(config: dict, defaults_path: Path) -> bool:
    if not defaults_path.is_file():
        return False
    defaults = load_yaml(defaults_path)
    if not isinstance(defaults, dict):
        return False
    incoming = defaults.get("discord")
    if not isinstance(incoming, dict):
        return False
    discord = config.get("discord")
    if not isinstance(discord, dict):
        config["discord"] = dict(incoming)
        return True
    changed = False
    for key, val in incoming.items():
        if discord.get(key) != val:
            discord[key] = val
            changed = True
    return changed


def ensure_pollinations(config: dict, defaults_path: Path, *, merge_only: bool = False) -> bool:
    """Merge pollinations.defaults.yaml into Hermes config.

    When merge_only is True, register the Pollinations provider but do not
    override model.default / model.provider if already set (Hermes-existing users).
    """
    if not defaults_path.is_file():
        return False
    defaults = load_yaml(defaults_path)
    if not isinstance(defaults, dict):
        return False

    changed = False

    incoming = defaults.get("custom_providers")
    if isinstance(incoming, list) and incoming:
        existing = config.get("custom_providers")
        if not isinstance(existing, list):
            existing = []
            config["custom_providers"] = existing
        names = _provider_names(existing)
        for entry in incoming:
            if isinstance(entry, dict) and entry.get("name") not in names:
                existing.append(entry)
                names.add(str(entry["name"]))
                changed = True
            elif isinstance(entry, dict) and entry.get("name") == "pollinations":
                for i, cur in enumerate(existing):
                    if isinstance(cur, dict) and cur.get("name") == "pollinations":
                        if cur != entry:
                            existing[i] = entry
                            changed = True
                        break

    model_defaults = defaults.get("model")
    if isinstance(model_defaults, dict) and not merge_only:
        model = config.setdefault("model", {})
        if not isinstance(model, dict):
            model = {}
            config["model"] = model
        for key in ("default", "provider"):
            if key in model_defaults and model.get(key) != model_defaults[key]:
                model[key] = model_defaults[key]
                changed = True
        if "base_url" in model and model.get("provider", "").startswith("custom:"):
            model.pop("base_url", None)
            changed = True

    if not merge_only:
        fallbacks = defaults.get("fallback_providers")
        if isinstance(fallbacks, list) and config.get("fallback_providers") != fallbacks:
            config["fallback_providers"] = fallbacks
            changed = True

    return changed


def ensure_external_dir(config: dict, skills_path: str) -> bool:
    skills = config.setdefault("skills", {})
    if not isinstance(skills, dict):
        skills = {}
        config["skills"] = skills
    dirs = skills.setdefault("external_dirs", [])
    if not isinstance(dirs, list):
        dirs = []
        skills["external_dirs"] = dirs
    normalized = str(Path(skills_path).expanduser().resolve())
    if normalized in [str(Path(d).expanduser().resolve()) for d in dirs]:
        return False
    dirs.append(normalized)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nora-root", type=Path, required=True)
    parser.add_argument("--hermes-home", type=Path, default=Path.home() / ".hermes")
    parser.add_argument("--skip-config", action="store_true")
    parser.add_argument("--skip-soul", action="store_true")
    parser.add_argument(
        "--merge-only",
        action="store_true",
        help="Hermes-existing: wire SOUL/skills/discord; keep user's LLM provider",
    )
    args = parser.parse_args()

    nora_root = args.nora_root.expanduser().resolve()
    hermes_home = args.hermes_home.expanduser().resolve()
    soul_src = nora_root / "hermes" / "SOUL.md"
    skills_dir = nora_root / "skills"
    config_path = hermes_home / "config.yaml"

    if not soul_src.is_file():
        raise SystemExit(f"Missing {soul_src}")
    if not skills_dir.is_dir():
        raise SystemExit(f"Missing {skills_dir}")
    if not config_path.is_file():
        raise SystemExit(f"Hermes config not found: {config_path}")

    hermes_home.mkdir(parents=True, exist_ok=True)

    if not args.skip_soul:
        dest = hermes_home / "SOUL.md"
        if dest.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = hermes_home / f"SOUL.md.bak.{stamp}"
            shutil.copy2(dest, backup)
            print(f"  backed up existing SOUL → {backup.name}")
        shutil.copy2(soul_src, dest)
        print(f"  ✓ Installed SOUL.md → {dest}")

    if not args.skip_config:
        config = load_yaml(config_path)
        changed = False
        if ensure_external_dir(config, str(skills_dir)):
            changed = True
            print(f"  ✓ Added skills.external_dirs → {skills_dir}")
        if ensure_pollinations(
            config,
            nora_root / "hermes" / "pollinations.defaults.yaml",
            merge_only=args.merge_only,
        ):
            changed = True
            if args.merge_only:
                print("  ✓ Pollinations provider registered (kept your model.default / provider)")
            else:
                print("  ✓ Model provider → Pollinations (custom:pollinations / kimi)")
        if ensure_discord(config, nora_root / "hermes" / "discord.defaults.yaml"):
            changed = True
            print("  ✓ Discord → auto_thread off (use your threads; @mention inside)")
        if changed:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = hermes_home / f"config.yaml.bak.{stamp}"
            shutil.copy2(config_path, backup)
            dump_yaml(config_path, config)
            print(f"  ✓ Updated config.yaml (backup: {backup.name})")
        else:
            print("  ✓ config.yaml already wired for Nora")

    env_path = nora_root / ".env"
    has_pollen = False
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith(
                ("POLLINATIONS_API_KEY=", "POLLINATIONS_KEY=", "POLLENATIONS_API_KEY=")
            ):
                _, _, val = s.partition("=")
                has_pollen = bool(val.strip())
                break

    print()
    print("Discord + persona:")
    print("  • SOUL.md loads fresh every message — no restart required for voice changes")
    print("  • Skills cache may need: hermes gateway restart  (if gateway is running)")
    print("  • Gateway must be running with DISCORD_BOT_TOKEN in ~/.hermes/.env")
    print()
    print("LLM (Pollinations):")
    if has_pollen:
        print("  • POLLINATIONS_API_KEY found in nora/.env — run activate.sh to sync .env")
    else:
        print("  • Add POLLINATIONS_API_KEY to nora/.env from https://enter.pollinations.ai")
        print("    (sign in with GitHub: murderszn), then re-run ./scripts/activate.sh")
    print()
    print("Verify:")
    print("  hermes config          # model should be custom:pollinations / kimi")
    print("  hermes gateway status")
    print("  hermes chat -z 'Who are you?'   # Nora voice via Pollinations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())