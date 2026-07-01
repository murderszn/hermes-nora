---
name: safe-patch
description: Re-read-before-patch workflow for file edits. Use before patch, search_replace, or skill_manage write_file when content may have changed.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [patch, edit, files, verification]
    related_skills: [background-safe-edits, shell-cross-platform]
---

# Safe patch

## Workflow

1. **Read** the target file (or the exact region) immediately before editing.
2. **Confirm** `old_string` exists verbatim — whitespace, indentation, line endings.
3. **Apply** one logical change per patch when possible.
4. **Verify** — re-read the changed region or run a quick syntax/test check.
5. **Report** what changed in one line; include path and line range if helpful.

## No-op detection

Stop and re-read if:

- `old_string` and `new_string` would be identical
- `old_string` not found (file drifted)
- Multiple ambiguous matches — widen context in `old_string`

## Background sessions

In background-reviewed runs, `patch` and `read_file` may be blocked. Prefer:

- Capturing file content in the parent context before spawning
- `write_file` with full content when policy allows
- Foreground execution for multi-hunk edits

## Checklist

- [ ] File read in this turn (not from stale memory)
- [ ] Patch applied without error
- [ ] Post-patch read or test confirms intent
- [ ] No secrets committed or logged