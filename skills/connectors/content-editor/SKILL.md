---
name: content-editor
description: Long-form, image, and video content pipelines — draft, edit, format, publish prep. Use for newsletters, video notes, social assets, and editorial workflows.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [content, video, image, editorial, newsletter, connector]
    related_skills: [marketer, assistant, media-server]
---

# Content editor connector

## Scope

Shape content from raw material to publish-ready — Saturday newsletter pattern from Nora docs.

## Pipelines

### Long-form

1. Ingest outline or transcript
2. Structure: lede, sections, CTA
3. Pass: clarity → tone → length target
4. Export markdown, docx, or Gmail draft

### Image

- Crop/sizing notes for social aspect ratios
- Alt text and captions
- Hand heavy pixel work to external tools; Nora specs and filenames

### Video

- Chapter markers from transcript
- Title/description/thumbnail brief
- B-roll shot list if user provides source notes

## Newsletter schedule

User prepares substance; Nora:

1. Assembles draft in agreed template
2. Queues send via Gmail API on cron (**monitoring-briefing**)
3. Confirms send log after run

## Skills to combine

- `docx`, `pptx` for formatted output
- `marketer` for subject lines and social teasers
- `media-server` for library paths and transcoding hooks

## Don't

- Publish without approval
- Use copyrighted assets without license
- Promise video renders without ffmpeg/tool confirmation