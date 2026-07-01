---
name: background-safe-edits
description: Rules for file and tool work in background-reviewed Hermes sessions. Use when spawning subagents, cron workers, or any non-interactive profile with a restricted tool whitelist.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [background, subagent, delegation, patch, whitelist]
    related_skills: [safe-patch, delegation]
---

# Background-safe edits

## Constraint

Background paths often allow only **memory** and **skill** tools — not `patch`, `read_file`, or broad terminal.

## Do in the parent (before spawn)

- Read all files the child will need; pass excerpts in the task prompt
- Resolve paths and confirm binaries exist
- Break work into idempotent steps with clear done criteria

## Do in the child

- `write_file` for new skills or full-file rewrites when permitted
- `skill_manage` only after `skills_list()` confirms target
- Compact memory writes for durable facts only

## Avoid in background

- `patch` without a fresh read in the same context
- Chained shell that needs user consent mid-flight
- Assuming `gh`, submodule state, or skill dirs from prior sessions

## Escalation

Move to foreground or orchestrator delegation when:

- Multi-file refactors need `patch`
- Long-running installs need approval
- Tool whitelist errors appear in logs