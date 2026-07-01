# Nora skills library

Curated Hermes skills for Nora's capability matrix and connector packs. Enable by adding this directory to Hermes:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/nora/skills
```

Hermes discovers `**/SKILL.md` under each external dir.

## Ops foundation

| Skill | Path |
|-------|------|
| shell-cross-platform | `ops/shell-cross-platform/` |
| safe-patch | `ops/safe-patch/` |
| background-safe-edits | `ops/background-safe-edits/` |
| disk-and-repo-report | `ops/disk-and-repo-report/` |
| release-diagnostics | `ops/release-diagnostics/` |
| machine-control | `ops/machine-control/` |
| monitoring-briefing | `ops/monitoring-briefing/` |
| discord-hermes-setup | `ops/discord-hermes-setup/` |
| nora-onboard | `ops/nora-onboard/` |

## Core

| Skill | Path |
|-------|------|
| delegation | `core/delegation/` |
| persistent-memory | `core/persistent-memory/` |

## Connectors

| Pack | Path |
|------|------|
| Marketer | `connectors/marketer/` |
| Coder | `connectors/coder/` |
| Assistant | `connectors/assistant/` |
| Designer | `connectors/designer/` |
| Content editor | `connectors/content-editor/` |
| Therapist | `connectors/therapist/` |
| Document repo | `connectors/document-repo/` |
| Media server | `connectors/media-server/` |

## Helpers

Python utilities referenced by skills live in `../tools/`:

- `onboard.py` — interactive setup wizard
- `doctor.py` — health check
- `activate_nora.py` / `sync_env.py` — wire persona into Hermes
- `disk_and_repo_report.py`
- `release_diagnostics.py`

Shell entrypoints: `../scripts/onboard.sh`, `../scripts/doctor.sh`

Role map and persona notes: `../persona/roles.md`. Voice and identity: `../hermes/SOUL.md`.