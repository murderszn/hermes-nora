# 2026-06-27 Hermes-Nora learnings

Source: local Hermes log diagnostics from `C:\Users\jjohn\AppData\Local\hermes\logs\errors.log` and live dashboard recent-errors feed. Counts and root-cause categories are approximate; they are intended to drive repeatable fixes and skills.

## High-level themes

- Windows shell behavior is the dominant failure mode today.
- Background-review whitelisting blocks non-memory/skill tools.
- Several failures come from stale assumptions about paths and commands.

## Categories and corrective actions

### 1) Windows shell mismatch / quoting / PowerShell vs bash
- Observed errors: `Where-Object : The term 'C:\Users\jjohn\motion.DriveLetter' is not recognized`, `Missing expression after unary operator '-not'`, `Refresh : The term 'Refresh' is not recognized`.
- Root cause: PowerShell idioms, quoting, and chained commands are being mixed into bash contexts (or bash-style paths into PowerShell), and interpolation is producing malformed statements.
- Actions:
  - For dashboard ops, prefer an explicit PowerShell invocation or a Python helper, not mixed inline snippets.
  - For repo/disk enumeration across machines, prefer a Python helper script over inline `find … | while …` when shell is uncertain.
  - Add a `scripts/` helper per common operation (disk listing, git status, process cleanup) instead of ad-hoc one-liners.

### 2) Background-review tool whitelist blocks useful tools
- Observed errors: `non-whitelisted tool: patch`, `non-whitelisted tool: read_file`.
- Root cause: Non-interactive/background tool execution paths only allow memory/skill tools in this profile/perm model.
- Actions:
  - Prefer `write_file` in background-authored skills over `patch` where possible, or push file edits through explicit user-facing requests.
  - Capture file reads in `context` strings up front before starting background work, rather than reading files inside the child.
  - If a richer toolset is required, move work back to foreground or delegate with `role='orchestrator'` only if permitted by `delegation.max_spawn_depth` and tool allowances.

### 3) Timeouts and unconsented actions
- Observed error: `BLOCKED: Command timed out without user response. The user has NOT consented to this action.`
- Root cause: Long-running commands were blocked by timeout policy before user approval was obtained.
- Actions:
  - Set `notify_on_complete=true` and reasonable timeout budgets for bounded long tasks (builds, installs, migrations).
  - For truly open-ended commands (servers, watchers), use explicit background sessions with clear expectations.
  - Prefer brief heartbeat commands first when connectivity is uncertain; avoid issuing large multi-step shell chains blindly.

### 4) Stale/incorrect path assumptions
- Observed error: `ls: cannot access '/c/Users/jjohn/.hermes/skills/github/': No such file or directory`, `gh: command not found`.
- Root cause: Paths and CLIs were assumed to exist based on prior sessions or conventions, not verified at runtime.
- Actions:
  - Before using a path or binary, probe it in the same command sequence and fall back with an actionable error if missing.
  - Use `skills_list()` or filesystem discovery instead of hardcoding skill directories.
  - Document CLI dependencies (`git`, `gh`, `python`, `pip`, `ollama`, `nvm/npm`) in `README.md` install checklist.

### 5) Patch/skill matching / no-op errors
- Observed errors: `old_string and new_string are identical`, `Could not find a match for old_string in the file`, `file_content is required for 'write_file'`, `Skill 'X' not found in active profile 'default'`.
- Root cause: Scripted/templated edits were generated without first reading file state/skill registry, producing invalid tool inputs.
- Actions:
  - Do not regenerate edits blindly from prior patch recipes; re-read the file before `patch`.
  - Check skill registry with `skills_list()` before `skill_manage(action='write_file')`.
  - When using patch mode in a skill, require post-patch verification blocks.

### 6) Repo cleanliness and state assumptions
- Observed error: `fatal: no submodule mapping found in .gitmodules for path 'data-animation-skills'`.
- Root cause: Git repo state may include stale `.gitmodules`, untracked submodules, or incomplete clones.
- Actions:
  - Treat `.gitmodules` and submodules as opt-in and verify their presence before running submodule commands.
  - Repo setup scripts should handle absence gracefully or skip with explicit log lines.

### 7) Memory/capacity pressure
- Observed warning: `Adding this entry would exceed the limit. Consolidate now`.
- Root cause: Memory/tool/log volume exceeded budget in a session.
- Actions:
  - Use compact memory entries focused on durable facts only.
  - Avoid storing task progress and transient status in memory; use `todo` for in-turn planning and skills for repeatable workflows.

## Proposed skills to add

1. `windows-shell` — PowerShell vs bash selection rules, quoting, escaping, and cross-platform path conversion.
2. `safe-patch` — re-read-before-patch workflow, no-op detection, and verification checklist.
3. `hermes-background-safe-edits` — rules for what can/should be done in background-reviewed sessions (avoid patch/read_file unless absolutely required).
4. `hermes-disk-and-repo-report` — Python helper script that lists disks, git repo state, and active Hermes processes safely on Windows.
5. `hermes-release-diagnostics` — extract today’s warnings/errors from `errors.log` and turn them into a deterministic list of lessons + skill candidates.

## Proposed memory corrections

- Windows executions here need explicit shell assumptions recorded: prefer PowerShell for cmdlets, Python for filesystem/git enumeration, bash only for POSIX-valid commands.
- Record the local Hermes directory exactly: `C:\Users\jjohn\AppData\Local\hermes\`; don’t abstract it with `/~` conventions.
- Record Git CLI dependency for this machine as a confirmed requirement.
