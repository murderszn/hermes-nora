---
name: persistent-memory
description: Persistent ops memory hygiene — what to remember, what to forget, and when to author skills. Use for REMEMBER tasks and infrastructure learning.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, remember, skills, learning]
    related_skills: [release-diagnostics, safe-patch]
---

# Persistent memory

## REMEMBER role

Nora learns your infrastructure and never forgets how she fixed it last time — **if** memory stays disciplined.

## Store in memory

- Machine roles (hub vs laptop), OS, shell preferences
- Canonical paths (Hermes dir, project roots, dashboard port)
- Approved automation policies ("OK to prune Downloads over 30 days")
- Fix recipes that succeeded once and will recur

## Do not store in memory

- Transient task progress (use todos in-turn)
- Full file contents or log dumps
- Secrets, tokens, passwords
- Guesses that weren't verified

## Memory pressure

If consolidation warnings appear:

1. Merge duplicate facts
2. Move repeatable workflows into `skills/` via `skill_manage`
3. Archive stale entries

## Skill generation trigger

Author a new skill when:

- Same multi-step workflow requested twice
- `release-diagnostics` surfaces a repeat error class
- User says "remember how to do this"

Skill beats memory for **procedure**; memory beats skill for **facts**.

## User profile

Record communication preferences lightly:

- Brief vs verbose
- Preferred channels (Discord vs Gmail)
- Approval style for destructive ops

## Verification

Before writing memory:

- Is it durable across sessions?
- Is it under char limits?
- Would a future Nora act correctly from this alone?