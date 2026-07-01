---
name: shell-cross-platform
description: Pick the right shell, quoting, and path style on macOS, Linux, and Windows. Use when running terminal commands, enumerating files, git/gh/pip, or when PowerShell and bash get mixed.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [shell, bash, powershell, terminal, windows, cross-platform]
    related_skills: [disk-and-repo-report, safe-patch]
---

# Cross-platform shell

## When to use

- Any `execute_command` / terminal invocation
- Disk, process, network, or repo enumeration
- User is on Windows and commands fail with PowerShell/bash confusion

## Selection rules

| Construct | Shell |
|-----------|-------|
| `Get-*`, `-not`, cmdlets | PowerShell: `powershell -NoProfile -Command "..."` |
| `ls`, `find`, `grep`, POSIX pipes | Default terminal shell (often bash on Windows via MSYS) |
| Mixed or unclear | Split into two commands **or** implement in Python |

## Paths

- **macOS/Linux:** `/Users/name/...`, `~/...`
- **Windows native:** `C:\Users\name\...`
- **Windows MSYS/bash:** `/c/Users/name/...`
- Never assume `~/.hermes/skills/<category>/` exists — list or use `skills_list()` first.

## Quoting

- PowerShell from Python: prefer single-quoted outer wrapper; escape inner `'` as needed.
- Bash from Python: single-quote whole snippets to avoid `$` expansion.
- No JavaScript-style backtick templates inside shell strings.

## Recommendations

- **Python** — filesystem summaries, git status across repos, parsing output
- **PowerShell** — disk, network, Windows services
- **Bash** — simple POSIX file ops on Unix or MSYS
- Confirm `gh`, `git`, `python3` in PATH before use; fail with an actionable install hint.

## Pitfalls

1. Piping PowerShell into bash (or vice versa) in one line
2. Using `Refresh` or other cmdlets as bare words in bash
3. Hardcoding another machine's username or drive letter