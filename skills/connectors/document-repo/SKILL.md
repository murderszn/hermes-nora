---
name: document-repo
description: Indexed knowledge base — ingest docs, semantic search, citations. Use for "what did we decide," handbook queries, and repo documentation.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docs, knowledge, search, citations, connector]
    related_skills: [persistent-memory, coder]
---

# Document repo connector

## Scope

Turn scattered markdown, PDFs, and notes into **queryable knowledge** with citations — local first.

## Ingest

Supported starting points:

- Repo `docs/`, `learnings/`, README trees
- User-provided folders (read-only scan)
- Exported Notion/Obsidian markdown if synced locally

Steps:

1. Inventory files — respect `.gitignore`
2. Chunk by heading or page
3. Store index metadata: path, title, modified date
4. Prefer ripgrep + structured summaries before external vector DB unless user has one wired

## Query workflow

1. Parse user question
2. Search index (rg, sqlite, or connected hub)
3. Answer with **citations**: `path:line` or doc section
4. Say "not in corpus" when missing — don't hallucinate policy

## Maintenance

- Re-index on user request after large doc drops
- Flag stale docs (>N days) in briefing optional section
- Propose moving repeat answers into skills

## Hermes integration

- `learnings/` in this repo is the seed corpus for Nora ops patterns
- Link new learnings after **release-diagnostics** cycles

## Don't

- Index secrets directories (`.env`, `auth.json`, credentials)
- Quote entire copyrighted books — fair-use summaries only