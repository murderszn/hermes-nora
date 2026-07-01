---
name: media-server
description: Media library management, transcoding, and streaming hooks. Use for Plex/Jellyfin libraries, ffmpeg jobs, and home media ops.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [media, plex, jellyfin, ffmpeg, streaming, connector]
    related_skills: [machine-control, monitoring-briefing, content-editor]
---

# Media server connector

## Scope

Organize, transcode, and monitor home media — tied to the hub machine that stays on.

## Library hygiene

1. Scan roots user configures (movies, tv, music)
2. Report orphans, duplicates (by size/hash sample), missing metadata
3. Propose rename to standard pattern — **no moves without approval**

## Transcoding

Before ffmpeg:

- Confirm `ffmpeg` in PATH
- Dry-run with `-t 5` segment when testing
- Schedule heavy jobs via **monitoring-briefing** when GPU/CPU should be idle

Common ops:

```bash
ffmpeg -i input.mkv -c:v libx264 -crf 20 -c:a aac output.mp4
```

Adapt codecs to user hardware (NVENC, VideoToolbox).

## Streaming hooks

- Plex/Jellyfin: API tokens in env — never log them
- Report library refresh status
- Content-editor handoff for chapter art or descriptions

## Dashboard

Wire library path, last scan, active transcodes into local dashboard panels when available.

## Don't

- Delete source media without explicit approval and backup confirmation
- Run transcodes that saturate disk — check **disk-and-repo-report** first