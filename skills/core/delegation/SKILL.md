---
name: delegation
description: Ops task multiplication via Hermes subagents and orchestrator patterns. Use for parallel pipelines, isolated terminals, and zero-context-cost fan-out.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegate, subagent, orchestrator, parallel]
    related_skills: [background-safe-edits, machine-control]
---

# Delegation

## DELEGATE role

Use subagents when work is **parallelizable**, **long-running**, or needs a **clean context** — not for trivial one-liners you can do in the parent turn.

## When to delegate

| Signal | Action |
|--------|--------|
| Independent lanes (research + code + write) | Spawn children per lane |
| Large repo scan | Child with narrow prompt + paths |
| Repeatable RPC script | Child runs script; parent aggregates JSON |
| User wants progress while away | Background child + notify_on_complete |

## When not to delegate

- Single file edit with context already loaded
- Quick `git status` or disk check
- User is mid-conversation debugging — keep continuity

## Child prompt recipe

```
Goal: <one sentence>
Done when: <verifiable criteria>
Paths: <explicit list>
Constraints: <read-only | no patch | timeout N>
Return: <bullet summary + artifacts paths>
```

Pass file excerpts upfront — don't assume child can `read_file` in background mode.

## Orchestrator rules

- Discover available profiles before assigning (`hermes profile list` or ask user)
- Don't invent profile names the dispatcher won't recognize
- Parent summarizes; child executes
- Respect `delegation.max_spawn_depth` and concurrency limits

## Pitfalls

- Spawning a child to avoid reading a file in the parent
- Identical tasks duplicated across children
- No done criteria — children wander