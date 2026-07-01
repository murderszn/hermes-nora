---
name: assistant
description: Calendar, inbox triage, daily briefings, and async task routing. Use for personal ops, email, scheduling, and "what's on my plate."
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [assistant, email, calendar, briefing, connector]
    related_skills: [monitoring-briefing, marketer]
---

# Assistant connector

## Scope

Human 2.0 layer — triage the noise, surface what matters, route work to other connectors.

## Inbox triage

When Gmail or Himalaya is connected:

1. Classify: **action**, **FYI**, **defer**, **ignore**
2. Draft replies for **action** — don't send without approval
3. Batch FYI into a single summary
4. Propose filters or labels for repeat senders

Dedicated Nora inbox (`nora.*@`) = audit trail + calm async channel.

## Daily briefing

Combine **monitoring-briefing** machine status with:

- Calendar next 24–48h (if connected)
- Unread action emails count
- Open tasks user mentioned in last session

Keep under one screen on mobile.

## Scheduling

- Confirm timezone before proposing times
- Offer 2–3 slots for human meetings; cron for machine tasks
- Respect "one channel first" — don't duplicate alerts on Discord and email without reason

## Handoffs

| Ask type | Route to |
|----------|----------|
| Code fix | coder |
| Deck or doc | content-editor / docx / pptx skills |
| Campaign | marketer |
| Feelings / reflection | therapist (non-clinical) |

## Don't

- Send email or calendar invites without approval
- Store full email bodies in memory — summaries only