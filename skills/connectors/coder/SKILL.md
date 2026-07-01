---
name: coder
description: Repo-aware dev workflows — implement, review, test, deploy. Use for coding, debugging, PRs, and shipping software.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding, dev, git, pr, deploy, connector]
    related_skills: [safe-patch, shell-cross-platform, delegation]
---

# Coder connector

## Scope

Build and fix software on the user's machine — read repo before write, match existing style, run tests when available.

## Workflow

1. **Read** — tree, entry points, tests, CI config
2. **Plan** — smallest change that satisfies the ask
3. **Implement** — `safe-patch` discipline
4. **Verify** — lint, unit tests, or smoke command the repo already uses
5. **Summarize** — diff intent, commands run, follow-ups

## PR review mode

When reviewing a PR or diff:

- Correctness and edge cases first
- Security (secrets, injection, auth) second
- Style nits last
- Verdict: approve / comment / request changes with concrete fixes

## Deploy

Never deploy to production without explicit approval. Staging dry-runs OK when user has pre-authorized.

Record deploy commands in skills if they're repo-specific and repeated.

## Delegation

Large refactors: parent plans, child implements per package or directory via **delegation**.

## Pitfalls

- Editing without reading (violates safe-patch)
- Adding dependencies the repo doesn't use
- Assuming CI passes without running local checks