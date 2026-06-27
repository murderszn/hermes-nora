---
name: windows-shell
description: Prefer the correct shell and quoting on this Windows machine. Use this whenever you need to run external commands, enumerate files, or touch git/gh/pip processes.
triggers:
  - shell
  - bash
  - powershell
  - terminal
  - command
---

# Windows shell rules

## Selection rules
- If the command uses PowerShell-only constructs (`Get-NetTCPConnection`, `Get-Disk`, `-not` unary checks), invoke it through `powershell -NoProfile -Command "<snippet>"` or create a `.ps1` and run it.
- If the command uses POSIX constructs (`ls`, `find`, `grep`), run it via the terminal's default shell (`bash`) and use MSYS-style `/c/Users/jjohn/...` paths.
- If the command mixes both shells, split it into two commands or implement it in Python instead.

## Quoting / escaping
- PowerShell: wrap wrapped snippets in single quotes when interpolating from Python, and escape nested single quotes with `'"'"'` if needed.
- Bash: prefer single quotes for whole commands when embedding in Python strings to avoid `$` expansion.
- Avoid arbitrary backtick substitution like `` `esc(...)` `` inside bash snippets; these do not behave like JS template literals.

## Paths
- MSYS-style: `/c/Users/jjohn/...`
- Native Windows-style: `C:\Users\jjohn\...`
- Do not assume `~/.hermes/skills/github/` exists; check with filesystem listing first.

## Recommendations
- Prefer Python for filesystem/git/repo summaries.
- Prefer PowerShell for system/network/disk status.
- Prefer bash for simple POSIX file ops.
- Avoid running `gh` commands unless you have previously confirmed `gh` is in PATH for this machine.
