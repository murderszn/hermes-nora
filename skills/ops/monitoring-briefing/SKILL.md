---
name: monitoring-briefing
description: Always-on monitoring — health checks, cron scheduling, morning briefings, incident summaries. Use for WATCH tasks and plain-language schedules.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [monitoring, cron, schedule, briefing, watch]
    related_skills: [disk-and-repo-report, release-diagnostics, machine-control]
---

# Monitoring and briefing

## WATCH role

Natural-language scheduling for work that should happen **unattended** through the Hermes gateway.

## Good cron candidates

- Disk space threshold alerts
- Log rotation and stale download cleanup
- Git remote drift checks
- Gateway / Discord bridge health
- Newsletter or digest sends (with content ready)
- Idle GPU jobs (Folding@home, batch inference) when user is away

## Briefing template

**Morning / on-demand briefing:**

```
Status: <green|yellow|red>
Gateway: <up|down> · Last error: <none|one-liner>
Disk: <worst volume %>
Cron: <ran OK | N failures> since last briefing
Channels: <discord/gmail status>
Needs you: <bullet list or "nothing">
```

Pull data via `release-diagnostics`, `disk-and-repo-report`, and gateway state files.

## Scheduling phrasing

When user says "every morning at 7" or "when disk is above 90%":

1. Confirm timezone (`timezone` in Hermes config)
2. Propose concrete cron/gateway job text
3. Start read-only; escalate to destructive only with approval

## Incident summary

After failures:

1. What broke (timestamp, component)
2. Blast radius
3. What Nora already tried
4. Recommended human action
5. Whether to add a skill or memory entry so it doesn't repeat

## Pitfalls

- Scheduling destructive cleanup without retention policy
- Briefings that dump raw logs — summarize and link paths instead