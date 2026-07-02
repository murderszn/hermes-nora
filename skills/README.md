# Nora skills library

Curated Hermes skills for Nora's capability matrix and connector packs. Enable by adding this directory to Hermes:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/hermes-nora/skills
```

Hermes discovers `**/SKILL.md` under each external dir.

## How this library is organized

Nora ships three skill families that stack on top of Hermes runtime:

- **ops** — foundation skills for safe edits, shell cross-platform behavior, machine control, monitoring, onboarding, diagnostics, disk/repo reporting, and release checks.
- **core** — cross-cutting Nora behaviors: persistent memory hygiene and sub-agent delegation patterns.
- **connectors** — role-specific packs that wrap ops and core skills into repeatable workflows for specific jobs (coder, assistant, marketer, etc.).

You can pull in the whole library, or wire up just one connector plus the ops skills it depends on. Each `SKILL.md` lists `related_skills` so you can see the dependency graph before you import it.

## Ops foundation

These are the skills Nora uses most. If you install nothing else, install these:

| Skill | Path | What it does |
|-------|------|--------------|
| shell-cross-platform | `ops/shell-cross-platform/` | POSIX vs PowerShell vs cmd quirks. Use this before any terminal command that needs to travel between Mac, Linux, and Windows. |
| safe-patch | `ops/safe-patch/` | Read the relevant code before editing. Prefer minimal edits, diff intent, and fallback restoration when a patch doesn't land. |
| background-safe-edits | `ops/background-safe-edits/` | Long-running file work in the background so the parent session stays responsive. |
| disk-and-repo-report | `ops/disk-and-repo-report/` | Scan disks and repos, surface orphans, duplicates, and drift without destructive moves. |
| release-diagnostics | `ops/release-diagnostics/` | Build, test, and version checks before shipping anything. |
| machine-control | `ops/machine-control/` | GPU, CPU, disk, process management; manage the local machine Nora has access to. |
| monitoring-briefing | `ops/monitoring-briefing/` | Schedule morning briefings, health checks, and incident summaries. |
| discord-hermes-setup | `ops/discord-hermes-setup/` | Step-by-step Discord bot + gateway wiring, including the thread workflow that avoids duplicate replies. |
| nora-onboard | `ops/nora-onboard/` | The interactive wizard flow: SOUL, Pollinations key, channel secrets, activate, gateway, doctor. |

## Core

| Skill | Path | What it does |
|-------|------|--------------|
| delegation | `core/delegation/` | Spawn isolated subagents with their own terminal sessions. Use for parallel work, read-through reviews, or long-running isolated jobs. |
| persistent-memory | `core/persistent-memory/` | What to save, what to forget, and how to condense experiences across sessions without leaking secrets or polluting future runs. |

## Connectors

Connectors are role packs. Each one composes ops and core skills into a repeatable workflow. Install the packs you actually use.

| Pack | Path | Best for |
|------|------|----------|
| Marketer | `connectors/marketer/` | Campaign briefs, copy variants, channel messaging, analytics summaries. |
| Coder | `connectors/coder/` | Repo-aware dev workflows: read before write, plan smallest change, run tests, summarize diff. |
| Assistant | `connectors/assistant/` | Inbox triage, daily briefings, calendar, async task routing. |
| Designer | `connectors/designer/` | Layout review, token tables, component specs, export lists for dev. |
| Content editor | `connectors/content-editor/` | Image, video, long-form pipelines. Hands off visuals to the designer when needed. |
| Therapist | `connectors/therapist/` | Reflective journaling and guided check-ins. Strictly non-clinical, local-first privacy. |
| Document repo | `connectors/document-repo/` | Indexed knowledge base with semantic search and citations. |
| Media server | `connectors/media-server/` | Plex/Jellyfin library hygiene, ffmpeg transcoding, streaming hooks. |

### How connectors compose

Connectors do not run in isolation. A typical flow:

1. **User asks for something** in their area (calendar, code, campaign).
2. Nora loads the matching connector's `SKILL.md` and reads its `related_skills` links.
3. She pulls the relevant **ops** and **core** skills into scope for the current task.
4. She executes using Hermes toolchains, records the outcome through **persistent-memory**, and surfaces results on the user's chosen channel.

If a connector feels heavy for what you actually need, trim it: remove the skill directory from Hermes, or edit its `SKILL.md` to remove unused branches.

## Install methods

### Full library

Add the Nora repo to Hermes:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/hermes-nora/skills
```

### Single connector

Point Hermes at a single connector folder instead:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/hermes-nora/skills/connectors/coder
```

Hermes still needs `core/delegation` and `core/persistent-memory` for subagents and memory. Add them explicitly if you pick a single connector.

### Shell quick path

From the Nora repo root, after clone:

```bash
cp -r skills ~/.nora/skills
```

Then add `~/.nora/skills` to Hermes `config.yaml`.

## Scripts and helpers

Python utilities referenced by skills live in `../tools/`:

- `onboard.py` — interactive setup wizard
- `doctor.py` — health check
- `activate_nora.py` / `sync_env.py` — wire persona into Hermes
- `disk_and_repo_report.py`
- `release_diagnostics.py`

Shell entrypoints: `../scripts/onboard.sh`, `../scripts/doctor.sh`, `../scripts/activate.sh`.

## Role map and persona notes

- Role map and when to switch connectors: `../persona/roles.md`
- Voice and identity: `../hermes/SOUL.md`
- Channel setup mechanics: `../persona/channels.md`, `../persona/hermes-setup.md`

## Don't

- Run a connector that touches external systems (send email, modify code, delete media) without explicit user approval.
- Store raw secrets or full email/message bodies in memory — summaries only.
- Assume the first variant is final. Draft, flag compliance concerns, propose the next step.
