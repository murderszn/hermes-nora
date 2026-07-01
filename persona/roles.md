# Nora roles

Nora is one persona with multiple **connector packs** — skill modules that shift her focus without changing who she is.

## Capability matrix (shipped)

| # | Tag | Role folder | Primary skills |
|---|-----|-------------|----------------|
| 01 | CONTROL | `skills/ops/machine-control` | Terminals, dashboards, file/system ops |
| 02 | REMEMBER | `skills/core/persistent-memory` | Memory hygiene, skill capture |
| 03 | WATCH | `skills/ops/monitoring-briefing` | Cron, health checks, briefings |
| 04 | DELEGATE | `skills/core/delegation` | Subagents, parallel pipelines |
| 05 | PERSONA | `hermes/SOUL.md` + all skills | Voice + curated library |
| 06 | OPEN | repo root | MIT — fork, extend, ship |

## Connector packs (roadmap → v0 library)

| Pack | Path | Triggers |
|------|------|----------|
| Marketer | `skills/connectors/marketer` | campaigns, copy, analytics |
| Coder | `skills/connectors/coder` | repos, PRs, deploy, debug |
| Assistant | `skills/connectors/assistant` | inbox, calendar, briefings |
| Designer | `skills/connectors/designer` | layout, tokens, handoff |
| Content editor | `skills/connectors/content-editor` | video, image, long-form |
| Therapist | `skills/connectors/therapist` | journaling, check-ins (non-clinical) |
| Document repo | `skills/connectors/document-repo` | knowledge base, search, cite |
| Media server | `skills/connectors/media-server` | libraries, transcode, streaming |

## Ops foundation (always on)

| Skill | Path |
|-------|------|
| Cross-platform shell | `skills/ops/shell-cross-platform` |
| Safe patch workflow | `skills/ops/safe-patch` |
| Background-safe edits | `skills/ops/background-safe-edits` |
| Disk & repo report | `skills/ops/disk-and-repo-report` |
| Release diagnostics | `skills/ops/release-diagnostics` |

## Enabling in Hermes

Point Hermes at this repo's `skills/` tree:

```yaml
skills:
  external_dirs:
    - /path/to/nora/skills
```

`hermes/SOUL.md` is loaded automatically when placed in the Hermes state directory or referenced by your persona setup.